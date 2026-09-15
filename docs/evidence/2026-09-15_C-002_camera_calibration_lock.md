# C-002 Camera Calibration — LOCKED AND VERIFIED

C-002 camera calibration is LOCKED and VERIFIED for NanoBot AprilTag pose verification.

This calibration is a measurement artifact for AprilTag pose calculation. It does not change NanoBot camera capture configuration.

## Verification

- Runtime machine: Orin Nano
- Image size: 1280 × 720
- OpenCV: 4.13.0
- Calibration target: C-001 ChArUco board
- Board: 7 × 5 squares, 30.0 mm square size, 22.0 mm marker size, DICT_4X4_50
- Images used: 15
- ChArUco corners per image: 24
- Images accepted: 15/15
- Independent calibration reproduction: PASS
- RMS reprojection error: 0.264113345 px
- Mean per-image error: 0.052850805 px
- Minimum per-image error: 0.041434412 px
- Maximum per-image error: 0.082929171 px

## Camera matrix

[[1379.4131519171663, 0.0, 637.8223484586773],
 [0.0, 1369.9367688931832, 344.3519013248128],
 [0.0, 0.0, 1.0]]

## Distortion coefficients

[-0.046457001964562414, 1.0761381379969828, -0.0041470943952415075, -0.011495976371470717, -3.965242928279385]

## Preserved artifact

Artifact: `config/camera_calibration/C-002_camera_calibration.json`

SHA-256: `9babdf22e7a20ae309ad84930e41b8c3b3f3f882f75a82d2a5f8542579793230`

The repository artifact hash matches the independently verified Orin artifact.

## Setpoint lock

C-002 is locked for AprilTag pose verification. Calibration values must not be changed without new controlled calibration and verification.

C-002 is not applied to NanoBot runtime camera configuration.

## Change control

Any calibration change requires controlled recalibration or verified replacement, independent reproducibility verification, updated evidence, artifact hash verification, and explicit re-lock before AprilTag pose use.
