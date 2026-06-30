#!/bin/bash

echo "🚀 NanoBot Bootstrap System v1 Starting..."

# -----------------------------
# 1. VERIFY REPOSITORY
# -----------------------------
if [ ! -d ".git" ]; then
  echo "❌ ERROR: Not inside NanoBot git repository"
  exit 1
fi

echo "✔ Git repository detected"

# -----------------------------
# 2. CORE STRUCTURE
# -----------------------------
mkdir -p .githooks
mkdir -p nodes/shared

echo "✔ Core directories ensured"

# -----------------------------
# 3. NODE IDENTITY (SAFE MODE)
# -----------------------------
if [ -f ".node_identity" ]; then
  NODE=$(cat .node_identity)
  echo "✔ Node identity loaded: $NODE"
else
  echo "⚠ No node identity found"
  echo "Enter node type (pi/orin/lenovo): "
  read NODE

  if [[ "$NODE" != "pi" && "$NODE" != "orin" && "$NODE" != "lenovo" ]]; then
    echo "❌ Invalid node type"
    exit 1
  fi

  echo "$NODE" > .node_identity
  echo "✔ Node identity set: $NODE"
fi

# -----------------------------
# 4. GIT HOOK CONFIG
# -----------------------------
git config core.hooksPath .githooks
echo "✔ Git hooks path set to .githooks"

# -----------------------------
# 5. HOOK EXECUTION PERMISSION
# -----------------------------
if [ -f ".githooks/pre-commit" ]; then
  chmod +x .githooks/pre-commit
  echo "✔ Pre-commit hook executable"
else
  echo "⚠ No pre-commit hook found"
fi

# -----------------------------
# 6. SYSTEM REPORT
# -----------------------------
echo ""
echo "🧠 NanoBot Node Ready"
echo "----------------------"
echo "Node: $NODE"
echo "Repo: OK"
echo "Hooks: ACTIVE"
echo "Structure: OK"
echo "----------------------"
echo "🚀 Bootstrap Complete"
