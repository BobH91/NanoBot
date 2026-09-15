#!/usr/bin/env bash
set -euo pipefail

# NanoBot Lenovo documentation workflow
#
# Purpose:
#   - verify repository state
#   - inspect evidence-document changes
#   - create/check the matching Obsidian vault note
#   - stage evidence + vault documentation
#   - STOP before commit/push
#
# This script does NOT:
#   - modify NanoBot runtime code
#   - restart services
#   - change Orin/Pi
#   - commit
#   - push

REPO="$HOME/NanoBot"
EVIDENCE_DOC="$REPO/docs/evidence/2026-09-14_orin_camera_problem_solution.md"
VAULT_NOTE="$REPO/vault/04_ai_chats/Orin_Camera_Performance_Problem_Solution.md"

cd "$REPO"

echo "=========================================="
echo "NANOBOT DOCUMENTATION WORKFLOW"
echo "=========================================="
echo "Machine: $(hostname)"
echo "Repository: $REPO"
echo
echo "Commit only after explicit verification."
echo

echo "=== 1. Repository status ==="
git status --short
echo

echo "=== 2. Diff check ==="
git diff --check
echo "git diff --check: PASS"
echo

echo "=== 3. Evidence document diff ==="

if git ls-files --error-unmatch "$EVIDENCE_DOC" >/dev/null 2>&1; then
    git diff -- "$EVIDENCE_DOC"
else
    echo "Evidence document is not tracked yet:"
    echo "$EVIDENCE_DOC"
fi

echo

echo "=== 4. Create/check vault note ==="

mkdir -p "$(dirname "$VAULT_NOTE")"

EXPECTED_NOTE="$(mktemp)"
trap 'rm -f "$EXPECTED_NOTE"' EXIT

cat > "$EXPECTED_NOTE" <<'EOF'
# Orin Camera Performance — Verified Problem and Solution

## Status

**VERIFIED / LOCKED**

Date: 2026-09-14
Machine: Jetson Orin Nano (`Nanobot`)
Verification ID: `ORIN-CAM-720P30-PROBLEM-SOLUTION`

## Verified Camera Baseline

- Device: `/dev/video0`
- Format: MJPG
- Resolution: 1280×720
- Configured FPS: 30
- Measured FPS: approximately 29.7–29.8 FPS
- Dropped frames: 0
- JPEG quality: 85
- Forced OpenCV `CAP_PROP_BUFFERSIZE=1`: **not used**

## Verified Performance Problem

During controlled testing, forcing:

`cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)`

reduced sustained camera capture performance.

Removing this forced buffer setting restored approximately 29.7–29.8 FPS with zero dropped frames.

No artificial 15 FPS limiter exists in the NanoBot camera capture loop.

## Historical 15.1 FPS Observation

A separate runtime observation reported approximately 15.1 FPS.

A subsequent controlled restart of `nanobot-webrtc.service` from a verified approximately 29.8 FPS state produced approximately 29.7–29.8 FPS with zero dropped frames.

Therefore, the historical 15.1 FPS observation remains documented as an anomaly with **no assigned cause**.

## Locked State

The camera baseline is locked at:

**`/dev/video0` / MJPG / 1280×720 / 30 FPS configured / approximately 29.7–29.8 FPS measured / 0 drops**

No camera code, V4L2 control, or runtime configuration should be changed without an explicitly authorized controlled change.

## Authoritative Engineering Record

Full evidence is maintained in the NanoBot Git repository:

`docs/evidence/2026-09-14_orin_camera_problem_solution.md`

Git commit:

`76bcdd0`

Commit message:

`docs: record Orin camera problem and verified solution`

## Historical Evidence

Original camera verification:

`docs/evidence/2026-09-09_orin_camera_1280x720_30fps_verification.md`

Historical 15.1 FPS observation:

`87e7f6b`

Preserved documentation patch SHA-256:

`8b14f76695201acc42dfb051eeb3b61b3430f9cb196d0162c8ad4bf2ca6a9017`
EOF

if [[ -e "$VAULT_NOTE" ]]; then
    if cmp -s "$EXPECTED_NOTE" "$VAULT_NOTE"; then
        echo "Vault note: UNCHANGED"
    else
        echo "ERROR: Existing vault note differs from expected content."
        echo "No overwrite performed."
        exit 1
    fi
else
    cp "$EXPECTED_NOTE" "$VAULT_NOTE"
    echo "Vault note created:"
    echo "  $VAULT_NOTE"
fi

echo

echo "=== 5. Verify vault note ==="
cat "$VAULT_NOTE"
echo

echo "=== 6. Stage evidence + vault documents ==="

git add "$EVIDENCE_DOC" "$VAULT_NOTE"

echo

echo "=== 7. Staged diff check ==="

git diff --cached --check
echo "Staged diff check: PASS"
echo

echo "=== 8. Staged changes ==="

git status --short
echo

echo "=== 9. Staged diff summary ==="

git diff --cached --stat
echo

echo "=== 10. Staged diff ==="

git diff --cached -- "$EVIDENCE_DOC" "$VAULT_NOTE"
echo

echo "=========================================="
echo "DOCUMENTATION STAGING COMPLETE"
echo "=========================================="
echo
echo "No commit was created."
echo "No push was performed."
echo "No runtime machine was changed."
echo
echo "Review the staged diff above."
echo "Commit only after explicit verification."
