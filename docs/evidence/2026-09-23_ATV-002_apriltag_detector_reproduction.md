# ATV-002 — AprilTag Detector Reproduction

## Status

**PASS**

## Purpose

Controlled reproduction of AprilTag detection and pose estimation on the
Orin Nano using the locked camera calibration and AprilTag configuration,
without modifying NanoBot runtime code, camera configuration, calibration,
or WebRTC.

## Environment

- Machine: Orin Nano
- Hostname: `Nanobot`
- Repository HEAD: `1652a12`
- Image source: NanoBot `/snapshot`
- Image resolution: 1280×720
- Python environment: `~/nanobot-apriltag-venv`
- AprilTag library: `pupil_apriltags 1.0.4.post11`
- OpenCV: 4.13.0.92

## Locked AprilTag Setpoints

- Family: `tag36h11`
- Target Tag ID: `0`
- Physical tag size: `0.150 m`
- Camera calibration: C-002
- Camera matrix: C-002 locked values
- Detector configuration:
  - `nthreads=2`
  - `quad_decimate=1.0`
  - `quad_sigma=0.0`
  - `refine_edges=1`
  - `decode_sharpening=0.25`

## Controlled Test Sequence

### I01

Image:

`/tmp/ATV-002-I01.jpg`

SHA-256:

`4c6651b5ef60050848cbda524a2bc40781a1af24f9bd559ac32d45e5a4305a48`

Result:

- Tag 0 not detected.
- Visual inspection showed approximately the top 1 inch of the physical
  tag was outside the image frame.

No detector parameters, calibration values, camera settings, or software
were changed in response.

### I02

The camera was moved farther back so the complete physical Tag 0 and
surrounding white space were visible.

Image:

`/tmp/ATV-002-I02.jpg`

SHA-256:

`ae1b5c5bb57058353e25966c5a9e593b2b9e9c2d8753f5cf386741cd22f0fa5b`

Result:

- Detections: 1
- Tag ID: 0
- Hamming: 0
- Decision margin: 75.278

Pose:

- X: -0.098248 m
- Y: -0.182906 m
- Z: 1.156616 m
- 3-D distance: 1.175103 m
- 3-D distance: 117.510 cm

## Verification Conclusion

**ATV-002 PASS.**

The Orin Nano successfully reproduced AprilTag detection and pose
estimation using:

- the locked `tag36h11` family,
- Tag ID 0,
- 150 mm physical tag size,
- the locked C-002 camera calibration,
- 1280×720 imagery,
- and the verified `pupil_apriltags` environment.

The I01 failure was associated with incomplete physical framing. After
moving the camera farther back, I02 produced a valid Tag 0 detection with
hamming 0 and a decision margin of 75.278.

The I02 pose distance is **not an absolute-accuracy result** and is not
compared against C-003 or C-004 because the camera position was changed
between those experiments.

No calibration correction, camera-setting change, detector-setting change,
runtime code change, service restart, or WebRTC change was made.

## Evidence Integrity

I01 SHA-256:

`4c6651b5ef60050848cbda524a2bc40781a1af24f9bd559ac32d45e5a4305a48`

I02 SHA-256:

`ae1b5c5bb57058353e25966c5a9e593b2b9e9c2d8753f5cf386741cd22f0fa5b`

## Next Controlled Milestone

Following evidence review, the next milestone is to define and verify the
minimal NanoBot AprilTag runtime integration using the already-proven
detector configuration. No runtime implementation is part of ATV-002.
