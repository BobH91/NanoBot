#!/usr/bin/env python3
"""
camera.py — Nanobot camera capture (Orin Nano)
Hardware:
  Logitech 720p USB camera
  /dev/video0, 960x544, MJPG, 30 fps

Provides a thread-safe FrameGrabber that continuously captures
frames in a background thread. Consumers (webrtc_server.py) call
get_frame() to get the latest JPEG bytes without blocking on capture.
"""

import logging
import sys
import threading
import time

import cv2
import numpy as np

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
DEVICE          = "/dev/video0"
CAPTURE_WIDTH   = 960
CAPTURE_HEIGHT  = 544
CAPTURE_FPS     = 30
FOURCC          = "MJPG"

# JPEG re-encode quality when consumers request compressed frames
JPEG_QUALITY    = 85

# How long to wait for first frame before raising (seconds)
STARTUP_TIMEOUT = 5.0

LOG_LEVEL       = logging.INFO

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("camera")


# ──────────────────────────────────────────────
# Frame grabber
# ──────────────────────────────────────────────
class FrameGrabber:
    """
    Continuously captures frames from the camera in a daemon thread.

    Usage
    -----
    cam = FrameGrabber()
    cam.start()

    frame_bgr  = cam.get_frame()        # latest numpy BGR array, or None
    frame_jpeg = cam.get_jpeg()         # latest JPEG bytes, or None

    cam.stop()
    """

    def __init__(
        self,
        device: str       = DEVICE,
        width: int        = CAPTURE_WIDTH,
        height: int       = CAPTURE_HEIGHT,
        fps: int          = CAPTURE_FPS,
        fourcc: str       = FOURCC,
        jpeg_quality: int = JPEG_QUALITY,
    ):
        self._device       = device
        self._width        = width
        self._height       = height
        self._fps          = fps
        self._fourcc       = fourcc
        self._jpeg_quality = jpeg_quality

        self._cap: cv2.VideoCapture | None = None
        self._lock         = threading.Lock()
        self._frame: np.ndarray | None = None   # latest BGR frame
        self._frame_time   = 0.0                # monotonic timestamp
        self._running      = False
        self._thread: threading.Thread | None = None

        # Stats
        self._frame_count  = 0
        self._drop_count   = 0
        self._fps_measured = 0.0

    # ── Lifecycle ───────────────────────────────

    def start(self) -> None:
        """Open camera and start capture thread."""
        self._cap = self._open_camera()
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

        # Wait for first frame
        deadline = time.monotonic() + STARTUP_TIMEOUT
        while time.monotonic() < deadline:
            if self._frame is not None:
                log.info("Camera ready — first frame received.")
                return
            time.sleep(0.05)

        raise RuntimeError(
            f"Camera {self._device} opened but no frames received within "
            f"{STARTUP_TIMEOUT}s — check cable and V4L2 format."
        )

    def stop(self) -> None:
        """Stop capture thread and release camera."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._cap:
            self._cap.release()
            self._cap = None
        log.info("Camera released. Frames: %d  Drops: %d",
                  self._frame_count, self._drop_count)

    # ── Consumer API ────────────────────────────

    def get_frame(self) -> np.ndarray | None:
        """Return latest BGR numpy array, or None if not yet available."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def get_jpeg(self) -> bytes | None:
        """Return latest frame encoded as JPEG bytes."""
        frame = self.get_frame()
        if frame is None:
            return None
        ok, buf = cv2.imencode(
            ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, self._jpeg_quality]
        )
        return buf.tobytes() if ok else None

    def get_stats(self) -> dict:
        return {
            "frame_count":  self._frame_count,
            "drop_count":   self._drop_count,
            "fps_measured": round(self._fps_measured, 1),
            "width":        self._width,
            "height":       self._height,
        }

    @property
    def frame_time(self) -> float:
        """Monotonic timestamp of the most recent frame."""
        return self._frame_time

    # ── Internal ────────────────────────────────

    def _open_camera(self) -> cv2.VideoCapture:
        log.info("Opening %s  %dx%d  %s  %d fps …",
                 self._device, self._width, self._height,
                 self._fourcc, self._fps)

        cap = cv2.VideoCapture(self._device, cv2.CAP_V4L2)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera: {self._device}")

        cap.set(cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(*self._fourcc))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self._width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        cap.set(cv2.CAP_PROP_FPS,          self._fps)
        # Keep internal buffer minimal — we always want the latest frame
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Confirm what the driver actually gave us
        actual_w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        log.info("Camera opened: %dx%d @ %.1f fps", actual_w, actual_h, actual_fps)

        if actual_w != self._width or actual_h != self._height:
            log.warning(
                "Requested %dx%d but driver gave %dx%d — "
                "check MJPG support for this resolution.",
                self._width, self._height, actual_w, actual_h,
            )

        return cap

    def _capture_loop(self) -> None:
        fps_t0      = time.monotonic()
        fps_frames  = 0

        while self._running:
            ok, frame = self._cap.read()
            if not ok:
                log.warning("Frame read failed — retrying …")
                self._drop_count += 1
                time.sleep(0.01)
                continue

            now = time.monotonic()
            with self._lock:
                self._frame      = frame
                self._frame_time = now

            self._frame_count += 1
            fps_frames        += 1

            # Update measured FPS every second
            elapsed = now - fps_t0
            if elapsed >= 1.0:
                self._fps_measured = fps_frames / elapsed
                fps_frames = 0
                fps_t0     = now

    # ── Context manager ──────────────────────────

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()


# ──────────────────────────────────────────────
# Singleton (used by webrtc_server.py)
# ──────────────────────────────────────────────
_grabber: FrameGrabber | None = None
_grabber_lock = threading.Lock()


def get_grabber() -> FrameGrabber:
    global _grabber
    with _grabber_lock:
        if _grabber is None:
            _grabber = FrameGrabber()
            _grabber.start()
    return _grabber


def shutdown_grabber() -> None:
    global _grabber
    with _grabber_lock:
        if _grabber is not None:
            _grabber.stop()
            _grabber = None


# ──────────────────────────────────────────────
# CLI smoke test — saves 30 frames as JPEG
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import os

    out_dir = "/home/bob/nanobot/logs/camera_test"
    os.makedirs(out_dir, exist_ok=True)

    print(f"Nanobot camera.py — smoke test  (saving 30 frames to {out_dir})")

    with FrameGrabber() as cam:
        saved = 0
        while saved < 30:
            jpeg = cam.get_jpeg()
            if jpeg:
                path = os.path.join(out_dir, f"frame_{saved:03d}.jpg")
                with open(path, "wb") as f:
                    f.write(jpeg)
                saved += 1
                print(f"  saved {path}  ({len(jpeg):,} bytes)")
            time.sleep(1 / CAPTURE_FPS)

        print("Stats:", cam.get_stats())

    print("Done.")
    sys.exit(0)
