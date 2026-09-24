#!/usr/bin/env python3
"""
NanoBot AprilTag worker.

ATV-003 runtime integration component.

Design constraints:
- Never opens /dev/video0.
- Receives independent frame copies from the existing FrameGrabber.
- Uses the locked ATV-002 detector configuration.
- Loads camera intrinsics from canonical C-002.
- Maintains only the latest submitted frame.
- Maintains only the latest detection result.
- Detector exceptions do not escape the worker thread.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
from pupil_apriltags import Detector


# ---------------------------------------------------------------------------
# Locked ATV-003 / ATV-002 setpoints
# ---------------------------------------------------------------------------

TAG_FAMILY = "tag36h11"
TAG_ID = 0
TAG_SIZE_M = 0.150

DETECTOR_NTHREADS = 2
DETECTOR_QUAD_DECIMATE = 1.0
DETECTOR_QUAD_SIGMA = 0.0
DETECTOR_REFINE_EDGES = 1
DETECTOR_DECODE_SHARPENING = 0.25

EXPECTED_IMAGE_WIDTH = 1280
EXPECTED_IMAGE_HEIGHT = 720

C002_RELATIVE_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "camera_calibration"
    / "C-002_camera_calibration.json"
)

C002_EXPECTED_SHA256 = (
    "9babdf22e7a20ae309ad84930e41b8c3b3f3f882f75a82d2a5f8542579793230"
)


@dataclass(frozen=True)
class CameraCalibration:
    calibration_id: str
    image_width: int
    image_height: int
    fx: float
    fy: float
    cx: float
    cy: float


@dataclass(frozen=True)
class AprilTagResult:
    timestamp: float
    frame_time: Optional[float]
    detector_runtime_ms: float
    detected: bool
    tag_id: Optional[int]
    hamming: Optional[int]
    decision_margin: Optional[float]
    x_m: Optional[float]
    y_m: Optional[float]
    z_m: Optional[float]
    distance_m: Optional[float]
    error: Optional[str] = None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_c002_calibration(
    path: Path = C002_RELATIVE_PATH,
) -> CameraCalibration:
    """Load and validate the locked C-002 calibration artifact."""

    actual_sha256 = _sha256(path)
    if actual_sha256 != C002_EXPECTED_SHA256:
        raise RuntimeError(
            "C-002 SHA-256 mismatch: "
            f"expected {C002_EXPECTED_SHA256}, "
            f"got {actual_sha256}"
        )

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if data.get("calibration_id") != "C-002":
        raise RuntimeError("Calibration artifact is not C-002.")

    if data.get("status") != "COMPUTED_AND_REPRODUCED":
        raise RuntimeError(
            "C-002 status is not COMPUTED_AND_REPRODUCED."
        )

    image_size = data.get("image_size")
    if image_size != [EXPECTED_IMAGE_WIDTH, EXPECTED_IMAGE_HEIGHT]:
        raise RuntimeError(
            f"Unexpected C-002 image size: {image_size}"
        )

    matrix = data["camera_matrix"]

    return CameraCalibration(
        calibration_id="C-002",
        image_width=image_size[0],
        image_height=image_size[1],
        fx=float(matrix[0][0]),
        fy=float(matrix[1][1]),
        cx=float(matrix[0][2]),
        cy=float(matrix[1][2]),
    )


def create_detector() -> Detector:
    """Construct the detector using the locked ATV-002 configuration."""

    return Detector(
        families=TAG_FAMILY,
        nthreads=DETECTOR_NTHREADS,
        quad_decimate=DETECTOR_QUAD_DECIMATE,
        quad_sigma=DETECTOR_QUAD_SIGMA,
        refine_edges=DETECTOR_REFINE_EDGES,
        decode_sharpening=DETECTOR_DECODE_SHARPENING,
    )


def detect_frame(
    detector: Detector,
    calibration: CameraCalibration,
    frame,
    frame_time: Optional[float] = None,
) -> AprilTagResult:
    """
    Detect the locked target Tag 0 in one BGR camera frame.

    No detection is an explicit result; it never reuses a previous pose.
    """

    timestamp = time.time()
    started = time.perf_counter()

    try:
        if frame is None:
            raise ValueError("Frame is None.")

        height, width = frame.shape[:2]
        if width != EXPECTED_IMAGE_WIDTH or height != EXPECTED_IMAGE_HEIGHT:
            raise ValueError(
                f"Unexpected frame size: {width}x{height}; "
                f"expected {EXPECTED_IMAGE_WIDTH}x{EXPECTED_IMAGE_HEIGHT}"
            )

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        detections = detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=(
                calibration.fx,
                calibration.fy,
                calibration.cx,
                calibration.cy,
            ),
            tag_size=TAG_SIZE_M,
        )

        runtime_ms = (time.perf_counter() - started) * 1000.0

        target = next(
            (
                detection
                for detection in detections
                if int(detection.tag_id) == TAG_ID
            ),
            None,
        )

        if target is None:
            return AprilTagResult(
                timestamp=timestamp,
                frame_time=frame_time,
                detector_runtime_ms=runtime_ms,
                detected=False,
                tag_id=None,
                hamming=None,
                decision_margin=None,
                x_m=None,
                y_m=None,
                z_m=None,
                distance_m=None,
            )

        pose_t = target.pose_t
        x_m = float(pose_t[0][0])
        y_m = float(pose_t[1][0])
        z_m = float(pose_t[2][0])

        distance_m = (x_m * x_m + y_m * y_m + z_m * z_m) ** 0.5

        return AprilTagResult(
            timestamp=timestamp,
            frame_time=frame_time,
            detector_runtime_ms=runtime_ms,
            detected=True,
            tag_id=TAG_ID,
            hamming=int(target.hamming),
            decision_margin=float(target.decision_margin),
            x_m=x_m,
            y_m=y_m,
            z_m=z_m,
            distance_m=distance_m,
        )

    except Exception as exc:
        runtime_ms = (time.perf_counter() - started) * 1000.0

        return AprilTagResult(
            timestamp=timestamp,
            frame_time=frame_time,
            detector_runtime_ms=runtime_ms,
            detected=False,
            tag_id=None,
            hamming=None,
            decision_margin=None,
            x_m=None,
            y_m=None,
            z_m=None,
            distance_m=None,
            error=f"{type(exc).__name__}: {exc}",
        )


class AprilTagWorker:
    """
    Dedicated AprilTag worker.

    submit_frame() replaces any pending frame. There is never an
    unbounded frame queue.
    """

    def __init__(
        self,
        calibration: Optional[CameraCalibration] = None,
        detector: Optional[Detector] = None,
    ):
        self.calibration = calibration or load_c002_calibration()
        self.detector = detector or create_detector()

        self._condition = threading.Condition()
        self._pending_frame = None
        self._pending_frame_time: Optional[float] = None
        self._result: Optional[AprilTagResult] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        with self._condition:
            if self._running:
                return

            self._running = True
            self._thread = threading.Thread(
                target=self._run,
                name="nanobot-apriltag-worker",
                daemon=True,
            )
            self._thread.start()

    def submit_frame(
        self,
        frame,
        frame_time: Optional[float] = None,
    ) -> None:
        """
        Submit an independent frame copy.

        The caller owns the original frame. This worker stores only one
        pending frame at a time.
        """

        if frame is None:
            return

        frame_copy = frame.copy()

        with self._condition:
            if not self._running:
                raise RuntimeError("AprilTagWorker is not running.")

            self._pending_frame = frame_copy
            self._pending_frame_time = frame_time
            self._condition.notify()

    def latest_result(self) -> Optional[AprilTagResult]:
        with self._condition:
            return self._result

    def is_alive(self) -> bool:
        thread = self._thread
        return bool(thread and thread.is_alive())

    def stop(self, timeout: float = 2.0) -> None:
        with self._condition:
            self._running = False
            self._pending_frame = None
            self._pending_frame_time = None
            self._condition.notify()

        thread = self._thread
        if thread is not None:
            thread.join(timeout=timeout)

        if thread is not None and thread.is_alive():
            raise RuntimeError(
                "AprilTag worker did not stop within the timeout."
            )

        self._thread = None

    def _run(self) -> None:
        while True:
            with self._condition:
                while self._running and self._pending_frame is None:
                    self._condition.wait()

                if not self._running:
                    return

                frame = self._pending_frame
                frame_time = self._pending_frame_time

                self._pending_frame = None
                self._pending_frame_time = None

            result = detect_frame(
                self.detector,
                self.calibration,
                frame,
                frame_time,
            )

            with self._condition:
                self._result = result


if __name__ == "__main__":
    raise SystemExit(
        "apriltag_worker.py is a library/runtime component; "
        "use the ATV-003 verification script for testing."
    )
