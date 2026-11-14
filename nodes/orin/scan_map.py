"""
scan_map.py - AprilTag scan-and-map for a stationary NanoBot.

Grid frame (top-down, meters): origin = camera pan axis,
  +X = right of robot, +Y = straight ahead, Z = height above camera.
Camera frame (OpenCV / pupil_apriltags): x right, y down, z forward.

Physical angles: pan positive = camera turned right, tilt positive = camera
pitched up. Servo angles convert with config.SCAN_PAN_SIGN / SCAN_TILT_SIGN
(physical = sign * servo).
"""
import csv
import math
import os
import statistics
import threading
import time

import config

STATE_IDLE = "idle"
STATE_SCANNING = "scanning"
STATE_DONE = "done"
STATE_STOPPED = "stopped"
STATE_ERROR = "error"

CSV_FIELDS = (
    "stop", "pan_deg", "tilt_deg", "tag_id", "hamming", "decision_margin",
    "cam_x_m", "cam_y_m", "cam_z_m", "X_m", "Y_m", "Z_m", "range_m",
)


def camera_to_grid(x_m, y_m, z_m, pan_deg, tilt_deg):
    """
    Convert a tag position in the camera frame to the robot grid frame.

    pan_deg  : physical pan, positive = camera turned to the right
    tilt_deg : physical tilt, positive = camera pitched up
    Returns (X, Y, Z).
    """
    p = math.radians(pan_deg)
    t = math.radians(tilt_deg)
    f = y_m * math.sin(t) + z_m * math.cos(t)       # forward before pan
    gx = x_m * math.cos(p) + f * math.sin(p)
    gy = -x_m * math.sin(p) + f * math.cos(p)
    gz = -y_m * math.cos(t) + z_m * math.sin(t)
    return gx, gy, gz


def build_stops():
    """Serpentine list of (pan_deg, tilt_deg) physical angles."""
    pans = list(range(int(config.SCAN_PAN_MIN_DEG),
                      int(config.SCAN_PAN_MAX_DEG) + 1,
                      int(config.SCAN_PAN_STEP_DEG)))
    stops = []
    for row, tilt in enumerate(config.SCAN_TILT_ROWS_DEG):
        row_pans = pans if row % 2 == 0 else list(reversed(pans))
        for pan in row_pans:
            stops.append((pan, tilt))
    return stops


def aggregate(samples):
    """Mean grid position and spread per tag id."""
    by_id = {}
    for s in samples:
        by_id.setdefault(s["tag_id"], []).append(s)
    out = []
    for tag_id in sorted(by_id):
        rows = by_id[tag_id]
        xs = [r["X_m"] for r in rows]
        ys = [r["Y_m"] for r in rows]
        zs = [r["Z_m"] for r in rows]
        out.append({
            "tag_id": tag_id,
            "n": len(rows),
            "X_m": round(statistics.fmean(xs), 4),
            "Y_m": round(statistics.fmean(ys), 4),
            "Z_m": round(statistics.fmean(zs), 4),
            "X_std_m": round(statistics.pstdev(xs), 4),
            "Y_std_m": round(statistics.pstdev(ys), 4),
            "Z_std_m": round(statistics.pstdev(zs), 4),
        })
    return out


class _Abort(Exception):
    def __init__(self, state, message):
        super().__init__(message)
        self.state = state
        self.message = message


class ScanRunner:
    """
    Sweeps pan/tilt, waits for a fresh detection at each stop and records
    tag positions on the grid. Dependencies are injected so it can be tested
    without hardware:
      servos        : object with set(pan, tilt) and get_position() -> dict
      get_result    : callable returning the latest AprilTagResult (or None)
      estop_active  : callable returning True while the e-stop is latched
    """

    def __init__(
        self, servos, get_result, estop_active, stops=None, log_dir=None,
        motion_lock=None,
    ):
        self._servos = servos
        self._get_result = get_result
        self._estop_active = estop_active
        self._motion_lock = (
            motion_lock if motion_lock is not None else threading.RLock()
        )
        self._stops = list(stops) if stops is not None else build_stops()
        self._log_dir = log_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "logs")
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()
        self._estop_flag = threading.Event()
        self._thread = None
        self._state = STATE_IDLE
        self._index = 0
        self._samples = []
        self._timeouts = 0
        self._csv = None
        self._error = None
        self._started = None
        self._finished = None

    # -- public API -------------------------------------------------------

    def is_running(self):
        thread = self._thread
        return bool(thread and thread.is_alive())

    def start(self):
        with self._lock:
            if self.is_running():
                return False, "scan already running"
            if self._estop_active():
                return False, "e-stop active"
            self._stop_flag.clear()
            self._estop_flag.clear()
            self._state = STATE_SCANNING
            self._index = 0
            self._samples = []
            self._timeouts = 0
            self._csv = None
            self._error = None
            self._started = time.time()
            self._finished = None
            self._thread = threading.Thread(
                target=self._run, name="nanobot-scan", daemon=True)
            self._thread.start()
        return True, "scan started"

    def stop(self):
        self._stop_flag.set()

    def estop(self):
        """Latch an E-stop abort for this scan, independent of server reset."""
        self._estop_flag.set()
        self._stop_flag.set()

    def shutdown(self, timeout=3.0):
        """E-stop and join; return False if the scan thread remains alive."""
        self.estop()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=timeout)
            return not thread.is_alive()
        return True

    def status(self):
        with self._lock:
            samples = list(self._samples)
            snap = {
                "state": self._state,
                "stop_index": self._index,
                "stops_total": len(self._stops),
                "samples": len(samples),
                "timeouts": self._timeouts,
                "csv": self._csv,
                "error": self._error,
                "started": self._started,
                "finished": self._finished,
            }
        snap["tags"] = aggregate(samples)
        return snap

    # -- internals --------------------------------------------------------

    def _check_abort(self, allow_stopped=False):
        # E-stop takes priority and can never be bypassed.
        if self._estop_flag.is_set() or self._estop_active():
            raise _Abort(STATE_ERROR, "e-stop active")
        if not allow_stopped and self._stop_flag.is_set():
            raise _Abort(STATE_STOPPED, "stopped by user")

    def _set_servo_position(self, pan, tilt, allow_stopped=False):
        """Set a target under the shared motion gate, never bypassing E-stop."""
        with self._motion_lock:
            self._check_abort(allow_stopped=allow_stopped)
            self._servos.set(pan=pan, tilt=tilt)

    def _wait_arrival(self, servo_pan, servo_tilt, allow_stopped=False):
        deadline = time.monotonic() + config.SCAN_ARRIVE_TIMEOUT_S
        tol = config.SCAN_ARRIVE_TOL_DEG
        while True:
            self._check_abort(allow_stopped=allow_stopped)
            pos = self._servos.get_position()
            if (abs(pos["pan"] - servo_pan) <= tol
                    and abs(pos["tilt"] - servo_tilt) <= tol):
                return
            if time.monotonic() > deadline:
                raise RuntimeError(
                    "servos did not reach pan %.1f tilt %.1f"
                    % (servo_pan, servo_tilt))
            time.sleep(0.02)

    def _visit(self, index, pan, tilt):
        servo_pan = config.SCAN_PAN_SIGN * pan
        servo_tilt = config.SCAN_TILT_SIGN * tilt
        self._set_servo_position(servo_pan, servo_tilt)
        self._wait_arrival(servo_pan, servo_tilt)

        time.sleep(config.SCAN_SETTLE_S)
        ready = time.monotonic()
        threshold = ready + config.SCAN_FRESH_MARGIN_S
        deadline = ready + config.SCAN_RESULT_TIMEOUT_S

        result = None
        while True:
            self._check_abort()
            candidate = self._get_result()
            if (candidate is not None
                    and candidate.frame_time is not None
                    and candidate.frame_time > threshold):
                result = candidate
                break
            if time.monotonic() > deadline:
                break
            time.sleep(0.02)

        if result is None:
            with self._lock:
                self._timeouts += 1
            return

        pos = self._servos.get_position()
        pan_phys = config.SCAN_PAN_SIGN * pos["pan"]
        tilt_phys = config.SCAN_TILT_SIGN * pos["tilt"]
        rows = []
        for tag in result.tags:
            gx, gy, gz = camera_to_grid(
                tag.x_m, tag.y_m, tag.z_m, pan_phys, tilt_phys)
            rows.append({
                "stop": index,
                "pan_deg": round(pan_phys, 3),
                "tilt_deg": round(tilt_phys, 3),
                "tag_id": int(tag.tag_id),
                "hamming": tag.hamming,
                "decision_margin": round(tag.decision_margin, 2),
                "cam_x_m": round(tag.x_m, 4),
                "cam_y_m": round(tag.y_m, 4),
                "cam_z_m": round(tag.z_m, 4),
                "X_m": round(gx, 4),
                "Y_m": round(gy, 4),
                "Z_m": round(gz, 4),
                "range_m": round(math.hypot(gx, gy), 4),
            })
        with self._lock:
            self._samples.extend(rows)

    def _write_csv(self, samples):
        os.makedirs(self._log_dir, exist_ok=True)
        path = os.path.join(self._log_dir, time.strftime("scan_%Y%m%d_%H%M%S.csv"))
        with open(path, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(samples)
        return path

    def _run(self):
        state, error = STATE_DONE, None
        start_pos = None
        try:
            start_pos = self._servos.get_position()
            for index, (pan, tilt) in enumerate(self._stops):
                self._check_abort()
                with self._lock:
                    self._index = index
                self._visit(index, pan, tilt)
        except _Abort as abort:
            state, error = abort.state, abort.message
        except Exception as exc:
            state, error = STATE_ERROR, "%s: %s" % (type(exc).__name__, exc)

        # E-stop takes precedence even if it arrives as the scan loop ends.
        if self._estop_flag.is_set() or self._estop_active():
            state, error = STATE_ERROR, "e-stop active"

        # Never command a restoration movement after E-stop.
        if (start_pos is not None
                and not self._estop_flag.is_set()
                and not self._estop_active()):
            try:
                self._set_servo_position(
                    start_pos["pan"], start_pos["tilt"], allow_stopped=True)
                self._wait_arrival(
                    start_pos["pan"], start_pos["tilt"], allow_stopped=True)
            except _Abort as abort:
                state, error = abort.state, abort.message
            except Exception as exc:
                state = STATE_ERROR
                error = "restore failed: %s" % exc

        with self._lock:
            samples = list(self._samples)
        csv_path = None
        try:
            csv_path = self._write_csv(samples)
        except Exception as exc:
            state = STATE_ERROR
            error = "%s; csv failed: %s" % (error, exc) if error \
                else "csv failed: %s" % exc

        with self._lock:
            self._state = state
            self._error = error
            self._csv = csv_path
            self._finished = time.time()
