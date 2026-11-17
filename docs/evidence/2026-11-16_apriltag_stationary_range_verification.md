# AprilTag Stationary Range Verification

## Status

COMPLETED — REPEATABILITY VERIFIED; ABSOLUTE ACCURACY NOT ESTABLISHED

## Purpose

Follow-up stationary AprilTag distance verification at four tape-referenced
distances using the production Orin camera and AprilTag runtime.

This is separate from the original C-004 experiment.

## Locked Inputs

- Machine: Orin Nano
- Camera: 1280 × 720
- Tag family: tag36h11
- Tag ID: 0
- Physical tag size: 150 mm
- Pose tag size: 0.150 m
- Camera calibration: C-002
- Samples per distance: 10
- Camera configuration: unchanged
- Runtime source: unchanged

## Physical Reference

The four reference distances were reported as tape measurements.

The 150 cm and 250 cm measurements were explicitly confirmed as
camera lens to front plane of Tag 0.

The reference geometry for the earlier 100 cm and 203 cm measurements
was not separately reconfirmed.

## Results

All 40 samples detected Tag ID 0.
The worker remained alive and no detection errors were reported.

| Reference | Mean estimate | Minimum | Maximum | Spread | Error |
|---:|---:|---:|---:|---:|---:|
| 100 cm | 102.546 cm | 102.532 | 102.569 | 0.037 cm | +2.546 cm |
| 150 cm | 149.568 cm | 149.501 | 149.703 | 0.202 cm | -0.432 cm |
| 203 cm | 203.117 cm | 202.732 | 203.657 | 0.925 cm | +0.117 cm |
| 250 cm | 249.265 cm | 248.959 | 249.605 | 0.646 cm | -0.735 cm |

## Interpretation

- Detection: PASS, 40 of 40 samples.
- Worker stability: PASS.
- Repeatability: strong across all four tested distances.
- The 100 cm reference showed a positive difference of 2.546 cm.
- The other three estimates were closer to their reported references.
- Absolute accuracy is not established as a general specification.
- Tape reference uncertainty and measurement geometry remain relevant.

No calibration correction is justified by this dataset alone.

## Change Control

- C-002 calibration: unchanged.
- Physical tag size: unchanged.
- Camera configuration: unchanged.
- Runtime source: unchanged.
- Motor or servo movement: none commanded.
- Original C-004 evidence: unchanged.

## Conclusion

The test establishes successful stationary Tag 0 detection and
repeatable distance estimates at four reported reference distances.

It does not establish a universal absolute-distance accuracy specification.

The positive bias at 100 cm remains an observation for future
controlled verification.

C-002 remains locked.
