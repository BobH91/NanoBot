# C-004 — AprilTag Absolute-Distance Experiment

## Status

**COMPLETED — ABSOLUTE ACCURACY NOT ESTABLISHED**

## Purpose

Controlled experiment comparing AprilTag pose-derived 3-D distance with an independent physical distance measurement.

## Machine

- Orin Nano
- Runtime camera accessed through the existing `/snapshot` endpoint.
- No NanoBot runtime source, camera configuration, or service configuration was changed.

## Locked Inputs

- AprilTag family: `tag36h11`
- Tag ID: `0`
- Physical tag size: `150.0 mm`
- Pose tag size input: `0.150 m`
- Camera calibration: `C-002`
- Image size: `1280 × 720`
- Frames: 10

## Physical Reference

- Reference: lens center to physical center of Tag 0
- Measurement: straight-line tape measurement
- Measured distance: **113.3 cm (1.133 m)**
- Precision classification: **approximate**

## AprilTag Results

All 10 frames produced:

- Tag ID `0`
- Hamming `0`
- Valid pose

3-D pose-distance results:

- Mean: **110.820 cm**
- Minimum: **110.790 cm**
- Maximum: **110.849 cm**
- Range: **0.058 cm (0.58 mm)**

Comparison with physical reference:

- Physical reference: **113.300 cm**
- Mean computed distance: **110.820 cm**
- Difference: **-2.480 cm**
- Absolute difference: **2.480 cm**
- Relative difference: **2.189%**

## Interpretation

The AprilTag pose measurement is highly repeatable across the 10 stationary frames, with a 0.58 mm peak-to-peak range in computed 3-D distance.

Absolute accuracy is **not established** by this experiment. The independent physical reference was obtained with a tape measure and is therefore treated as approximate. The observed 2.480 cm difference is not sufficient evidence to modify the locked C-002 calibration.

No calibration adjustment was made.

## Evidence Preservation

The ten original C-004 JPEG captures are preserved in:

`config/apriltag_pose/C-004/`

Machine-readable results are preserved in:

`config/apriltag_pose/C-004/C-004_results.json`

The ten capture SHA-256 hashes were verified on Orin and independently matched after transfer to Lenovo.

## Change Control

- C-002 calibration: **unchanged**
- C-003 repeatability lock: **unchanged**
- Camera configuration: **unchanged**
- NanoBot runtime source: **unchanged**
- Runtime service configuration: **unchanged**

## Conclusion

C-004 provides a verified stationary 10-frame AprilTag pose-distance dataset and demonstrates strong measurement repeatability under this setup.

It does **not** establish an absolute-accuracy specification for NanoBot AprilTag pose.

A future absolute-accuracy experiment requires a more precise independently surveyed 3-D reference.
