# C-003 AprilTag Pose XYZ Repeatability Lock

Status: LOCKED AND VERIFIED

Purpose: Controlled repeatability verification of AprilTag XYZ pose estimation.

Machine: Orin Nano

Locked inputs:
- AprilTag family: tag36h11
- Tag ID: 0
- Physical tag size: 0.150 m (150.0 mm)
- Camera calibration: C-002
- Image size: 1280 x 720

Verification:
- 10/10 frames detected Tag ID 0
- Hamming distance: 0 for all frames
- X mean: -0.220202600 m
- X range: 0.000055000 m
- Y mean: 0.157281600 m
- Y range: 0.000042000 m
- Z mean: 1.088067200 m
- Z range: 0.000334000 m

Evidence artifact:
config/apriltag_pose/C-003_pose_repeatability.json

Artifact SHA-256:
f7ab1520f223e8e2b623913187156f7f7e3224554c76793eda4b43ac5c341d13

Interpretation:
This lock establishes repeatability of the measured pose under the controlled test conditions. It does not establish absolute pose accuracy because the camera-to-tag distance was not independently surveyed.

Change control:
The locked AprilTag family, ID, physical tag size, and C-002 calibration shall not be changed for this verification baseline without a new controlled verification and a new evidence record.

Runtime change:
No NanoBot runtime source or camera configuration was changed during C-003.
