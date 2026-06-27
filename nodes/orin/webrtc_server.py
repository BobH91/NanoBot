#!/usr/bin/env python3
"""
webrtc_server.py — Nanobot WebRTC server (Orin Nano)
Serves:
  - HTTP signalling endpoint  POST /offer  (SDP exchange)
  - HTTP status endpoint      GET  /status
  - WebRTC video track        (camera frames → browser)
  - WebRTC DataChannel        (browser → drive / pan/tilt commands)

DataChannel JSON protocol (browser → Nano):
  {"cmd": "drive",  "throttle": 0.5, "steering": 0.0}
  {"cmd": "pan",    "value": 30.0}
  {"cmd": "tilt",   "value": -15.0}
  {"cmd": "servo",  "pan": 0.0, "tilt": 0.0}
  {"cmd": "estop"}
  {"cmd": "estop_reset"}
  {"cmd": "ping"}

DataChannel JSON protocol (Nano → browser):
  {"event": "pong"}
  {"event": "estop", "active": true|false}
  {"event": "status", "pan": 0.0, "tilt": 0.0, "fps": 14.9, "connected": true}
"""

import asyncio
import fractions
import json
import logging
import signal
import sys
import time
import threading
from typing import Set

from aiohttp import web
from av import VideoFrame
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaRelay

from camera import get_grabber, shutdown_grabber
from servo import get_servos, shutdown_servos
from tcp_client import get_client, shutdown_client

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
HTTP_HOST       = "0.0.0.0"
HTTP_PORT       = 8080
VIDEO_CLOCKRATE = 90000
VIDEO_FPS       = 30
LOG_LEVEL       = logging.INFO

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/home/bob/nanobot/logs/webrtc_server.log"),
    ],
)
log = logging.getLogger("webrtc_server")

# ──────────────────────────────────────────────
# E-STOP state (global, latching)
# ──────────────────────────────────────────────
_estop_active = False
_estop_lock   = threading.Lock()


def estop_trigger() -> None:
    global _estop_active
    with _estop_lock:
        _estop_active = True
    get_client().estop()
    log.warning("E-STOP LATCHED")


def estop_reset() -> None:
    global _estop_active
    with _estop_lock:
        _estop_active = False
    get_client().stop()
    log.info("E-STOP reset")


def estop_is_active() -> bool:
    with _estop_lock:
        return _estop_active


# ──────────────────────────────────────────────
# Camera video track
# ──────────────────────────────────────────────
class CameraTrack(VideoStreamTrack):
    """
    Pulls frames from FrameGrabber and feeds them into the WebRTC pipeline.
    """
    kind = "video"

    def __init__(self):
        super().__init__()
        self._grabber   = get_grabber()
        self._pts       = 0
        self._time_base = fractions.Fraction(1, VIDEO_CLOCKRATE)
        self._frame_dur = VIDEO_CLOCKRATE // VIDEO_FPS

    async def recv(self) -> VideoFrame:
        # Pace output to VIDEO_FPS
        await asyncio.sleep(1 / VIDEO_FPS)

        frame_bgr = self._grabber.get_frame()

        if frame_bgr is None:
            # Send a black frame if camera not ready
            import numpy as np
            frame_bgr = __import__("numpy").zeros((544, 960, 3), dtype="uint8")

        # BGR → VideoFrame (aiortc expects RGB or YUV; we give BGR, av handles it)
        vf = VideoFrame.from_ndarray(frame_bgr, format="bgr24")
        vf.pts      = self._pts
        vf.time_base = self._time_base
        self._pts  += self._frame_dur
        return vf


# ──────────────────────────────────────────────
# DataChannel command handler
# ──────────────────────────────────────────────
def handle_command(raw: str, channel) -> None:
    """Parse and dispatch a DataChannel message from the browser."""
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        log.warning("Bad JSON on DataChannel: %r", raw)
        return

    cmd = obj.get("cmd", "").lower()

    # E-STOP blocks all motion commands
    if estop_is_active() and cmd not in ("estop_reset", "ping"):
        return

    client  = get_client()
    servos  = get_servos()

    if cmd == "drive":
        throttle = float(obj.get("throttle", 0.0))
        steering = float(obj.get("steering", 0.0))
        client.drive(throttle=throttle, steering=steering)

    elif cmd == "pan":
        servos.set_pan(float(obj.get("value", 0.0)))

    elif cmd == "tilt":
        servos.set_tilt(float(obj.get("value", 0.0)))

    elif cmd == "servo":
        servos.set(
            pan=float(obj.get("pan", 0.0)),
            tilt=float(obj.get("tilt", 0.0)),
        )

    elif cmd == "nudge_pan":
        servos.nudge_pan(float(obj.get("value", 0.0)))

    elif cmd == "nudge_tilt":
        servos.nudge_tilt(float(obj.get("value", 0.0)))

    elif cmd == "estop":
        estop_trigger()
        _send(channel, {"event": "estop", "active": True})

    elif cmd == "estop_reset":
        estop_reset()
        _send(channel, {"event": "estop", "active": False})

    elif cmd == "ping":
        _send(channel, {"event": "pong"})

    elif cmd == "stop":
        client.stop()

    else:
        log.warning("Unknown DataChannel cmd: %r", cmd)


def _send(channel, obj: dict) -> None:
    try:
        channel.send(json.dumps(obj))
    except Exception as exc:
        log.debug("DataChannel send error: %s", exc)


# ──────────────────────────────────────────────
# Peer connection manager
# ──────────────────────────────────────────────
pcs: Set[RTCPeerConnection] = set()
relay = MediaRelay()


async def offer_handler(request: web.Request) -> web.Response:
    """Handle SDP offer from browser, return SDP answer."""
    params = await request.json()
    offer  = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    log.info("New peer connection (total: %d)", len(pcs))

    # Add camera track
    camera_track = CameraTrack()
    pc.addTrack(relay.subscribe(camera_track))

    # Status push loop (runs while connection is open)
    status_channel = None

    @pc.on("datachannel")
    def on_datachannel(channel):
        nonlocal status_channel
        log.info("DataChannel opened: %s", channel.label)

        if channel.label == "control":
            status_channel = channel

            # Start periodic status push
            asyncio.ensure_future(_status_loop(channel))

            @channel.on("message")
            def on_message(message):
                handle_command(message, channel)

        elif channel.label == "estop":
            @channel.on("message")
            def on_estop_message(message):
                handle_command(message, channel)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log.info("Connection state: %s", pc.connectionState)
        if pc.connectionState in ("failed", "closed", "disconnected"):
            # Stop motors on disconnect
            if not estop_is_active():
                get_client().stop()
            pcs.discard(pc)
            await pc.close()

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp":  pc.localDescription.sdp,
            "type": pc.localDescription.type,
        }),
    )


async def _status_loop(channel) -> None:
    """Push status to browser every second."""
    grabber = get_grabber()
    servos  = get_servos()
    client  = get_client()

    while True:
        await asyncio.sleep(1.0)
        try:
            if channel.readyState != "open":
                break
            pos   = servos.get_position()
            stats = grabber.get_stats()
            _send(channel, {
                "event":     "status",
                "pan":       round(pos["pan"], 1),
                "tilt":      round(pos["tilt"], 1),
                "fps":       stats["fps_measured"],
                "connected": client.is_connected(),
                "estop":     estop_is_active(),
            })
        except Exception as exc:
            log.debug("Status loop error: %s", exc)
            break


async def status_handler(request: web.Request) -> web.Response:
    """Simple HTTP status endpoint for health checks."""
    grabber = get_grabber()
    servos  = get_servos()
    client  = get_client()
    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "camera":    grabber.get_stats(),
            "servo":     get_servos().get_position(),
            "rpi":       client.is_connected(),
            "estop":     estop_is_active(),
            "peers":     len(pcs),
        }),
    )


# ──────────────────────────────────────────────
# Startup / shutdown
# ──────────────────────────────────────────────
async def on_startup(app: web.Application) -> None:
    log.info("Starting subsystems …")
    get_grabber()   # starts camera capture thread
    get_servos()    # centres servos
    get_client()    # connects to RPi TCP server
    log.info("All subsystems ready.")


async def on_shutdown(app: web.Application) -> None:
    log.info("Shutting down …")
    # Close all peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    # Stop hardware
    get_client().stop()
    shutdown_client()
    shutdown_servos()
    shutdown_grabber()
    log.info("Shutdown complete.")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main() -> None:
    app = web.Application()
    app.router.add_post("/offer",  offer_handler)
    app.router.add_get("/status",  status_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Graceful SIGINT / SIGTERM
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, HTTP_HOST, HTTP_PORT)
    loop.run_until_complete(site.start())
    log.info("WebRTC server listening on http://%s:%d", HTTP_HOST, HTTP_PORT)
    log.info("Offer endpoint: POST http://192.168.4.90:%d/offer", HTTP_PORT)

    def _stop(sig, _):
        log.info("Signal %d received — stopping.", sig)
        loop.call_soon_threadsafe(loop.stop)

    signal.signal(signal.SIGINT,  _stop)
    signal.signal(signal.SIGTERM, _stop)

    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()


if __name__ == "__main__":
    main()
