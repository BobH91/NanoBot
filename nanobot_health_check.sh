#!/usr/bin/env bash
# NanoBot Health Check
# Checks git status and Syncthing status across all three NanoBot machines:
#   - Lenovo (local, controller node)
#   - Raspberry Pi 5 (motor control)
#   - Jetson Orin Nano (vision/high-level control)
#
# Usage: ./nanobot_health_check.sh
#
# Requires: passwordless SSH (key-based auth) already set up to
#           pi@192.168.4.153 and bob@192.168.4.90.

set -uo pipefail

REPO_DIR="NanoBot"
PI_HOST="pi@192.168.4.153"
ORIN_HOST="bob@192.168.4.90"
SYNCTHING_API_PORT=8384

BOLD="\033[1m"
GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"
RESET="\033[0m"

section() {
    echo ""
    echo -e "${BOLD}=== $1 ===${RESET}"
}

check_git_status_local() {
    if [ ! -d "$HOME/$REPO_DIR/.git" ]; then
        echo -e "${RED}✘ Repo not found at ~/$REPO_DIR${RESET}"
        return
    fi
    pushd "$HOME/$REPO_DIR" > /dev/null || return
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    LOCAL_SHA=$(git rev-parse --short HEAD 2>/dev/null)
    MODIFIED=$(git diff --name-only 2>/dev/null)
    MODIFIED_STAGED=$(git diff --cached --name-only 2>/dev/null)
    UNTRACKED=$(git status --porcelain 2>/dev/null | grep '^??' | sed 's/^?? //')
    AHEAD_BEHIND=$(git rev-list --left-right --count "origin/${BRANCH}...HEAD" 2>/dev/null)

    echo "Branch: $BRANCH ($LOCAL_SHA)"
    if [ -z "$MODIFIED" ] && [ -z "$MODIFIED_STAGED" ]; then
        echo -e "${GREEN}✔ No modified tracked files${RESET}"
    else
        echo -e "${RED}✘✘ MODIFIED TRACKED FILES (uncommitted drift risk):${RESET}"
        [ -n "$MODIFIED" ] && echo "$MODIFIED" | sed 's/^/    * /'
        [ -n "$MODIFIED_STAGED" ] && echo "$MODIFIED_STAGED" | sed 's/^/    * (staged) /'
        echo -e "${RED}    → Run 'git diff' on this file before ending the session.${RESET}"
    fi
    if [ -z "$UNTRACKED" ]; then
        echo -e "${GREEN}✔ No untracked files${RESET}"
    else
        UNTRACKED_COUNT=$(echo "$UNTRACKED" | wc -l)
        echo -e "${YELLOW}⚠ ${UNTRACKED_COUNT} untracked file(s) present${RESET}"
    fi
    if [ -n "$AHEAD_BEHIND" ]; then
        BEHIND=$(echo "$AHEAD_BEHIND" | awk '{print $1}')
        AHEAD=$(echo "$AHEAD_BEHIND" | awk '{print $2}')
        if [ "$BEHIND" = "0" ] && [ "$AHEAD" = "0" ]; then
            echo -e "${GREEN}✔ In sync with origin/${BRANCH}${RESET}"
        else
            echo -e "${YELLOW}⚠ ${AHEAD} ahead / ${BEHIND} behind origin/${BRANCH}${RESET}"
        fi
    fi
    popd > /dev/null || return
}

check_git_status_remote() {
    HOST="$1"
    REMOTE_CMD="
        if [ ! -d \"\$HOME/$REPO_DIR/.git\" ]; then
            echo 'MISSING_REPO'
            exit 0
        fi
        cd \"\$HOME/$REPO_DIR\" || exit 1
        BRANCH=\$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
        LOCAL_SHA=\$(git rev-parse --short HEAD 2>/dev/null)
        MODIFIED=\$(git diff --name-only 2>/dev/null)
        MODIFIED_STAGED=\$(git diff --cached --name-only 2>/dev/null)
        UNTRACKED=\$(git status --porcelain 2>/dev/null | grep '^??' | sed 's/^?? //')
        AHEAD_BEHIND=\$(git rev-list --left-right --count origin/\${BRANCH}...HEAD 2>/dev/null)
        echo \"BRANCH:\${BRANCH}\"
        echo \"SHA:\${LOCAL_SHA}\"
        echo \"AHEAD_BEHIND:\${AHEAD_BEHIND}\"
        echo \"MODIFIED_START\"
        echo \"\${MODIFIED}\"
        echo \"MODIFIED_END\"
        echo \"MODIFIED_STAGED_START\"
        echo \"\${MODIFIED_STAGED}\"
        echo \"MODIFIED_STAGED_END\"
        echo \"UNTRACKED_START\"
        echo \"\${UNTRACKED}\"
        echo \"UNTRACKED_END\"
    "
    OUTPUT=$(ssh -o ConnectTimeout=5 "$HOST" "$REMOTE_CMD" 2>&1)
    SSH_STATUS=$?

    if [ $SSH_STATUS -ne 0 ]; then
        echo -e "${RED}✘ SSH connection failed to $HOST${RESET}"
        echo "$OUTPUT" | sed 's/^/    /'
        return
    fi

    if echo "$OUTPUT" | grep -q "MISSING_REPO"; then
        echo -e "${RED}✘ Repo not found at ~/$REPO_DIR on $HOST${RESET}"
        return
    fi

    BRANCH=$(echo "$OUTPUT" | grep "^BRANCH:" | cut -d: -f2-)
    SHA=$(echo "$OUTPUT" | grep "^SHA:" | cut -d: -f2-)
    AHEAD_BEHIND=$(echo "$OUTPUT" | grep "^AHEAD_BEHIND:" | cut -d: -f2-)
    MODIFIED=$(echo "$OUTPUT" | sed -n '/MODIFIED_START/,/MODIFIED_END/p' | sed '1d;$d')
    MODIFIED_STAGED=$(echo "$OUTPUT" | sed -n '/MODIFIED_STAGED_START/,/MODIFIED_STAGED_END/p' | sed '1d;$d')
    UNTRACKED=$(echo "$OUTPUT" | sed -n '/UNTRACKED_START/,/UNTRACKED_END/p' | sed '1d;$d')

    echo "Branch: $BRANCH ($SHA)"
    if [ -z "$MODIFIED" ] && [ -z "$MODIFIED_STAGED" ]; then
        echo -e "${GREEN}✔ No modified tracked files${RESET}"
    else
        echo -e "${RED}✘✘ MODIFIED TRACKED FILES (uncommitted drift risk):${RESET}"
        [ -n "$MODIFIED" ] && echo "$MODIFIED" | sed 's/^/    * /'
        [ -n "$MODIFIED_STAGED" ] && echo "$MODIFIED_STAGED" | sed 's/^/    * (staged) /'
        echo -e "${RED}    → Run 'git diff' on this file before ending the session.${RESET}"
    fi
    if [ -z "$UNTRACKED" ]; then
        echo -e "${GREEN}✔ No untracked files${RESET}"
    else
        UNTRACKED_COUNT=$(echo "$UNTRACKED" | grep -c .)
        echo -e "${YELLOW}⚠ ${UNTRACKED_COUNT} untracked file(s) present${RESET}"
    fi
    if [ -n "$AHEAD_BEHIND" ]; then
        BEHIND=$(echo "$AHEAD_BEHIND" | awk '{print $1}')
        AHEAD=$(echo "$AHEAD_BEHIND" | awk '{print $2}')
        if [ "$BEHIND" = "0" ] && [ "$AHEAD" = "0" ]; then
            echo -e "${GREEN}✔ In sync with origin/${BRANCH}${RESET}"
        else
            echo -e "${YELLOW}⚠ ${AHEAD} ahead / ${BEHIND} behind origin/${BRANCH}${RESET}"
        fi
    fi
}

check_syncthing_local() {
    if ! command -v curl > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ curl not available, skipping${RESET}"
        return
    fi
    API_KEY="${SYNCTHING_API_KEY:-}"
    if [ -z "$API_KEY" ]; then
        RESP=$(curl -s -m 5 "http://localhost:${SYNCTHING_API_PORT}/rest/noauth/health" 2>/dev/null)
        if [ -n "$RESP" ]; then
            echo -e "${GREEN}✔ Syncthing responding on localhost:${SYNCTHING_API_PORT}${RESET}"
        else
            echo -e "${YELLOW}⚠ Could not reach Syncthing API (may need SYNCTHING_API_KEY set)${RESET}"
        fi
    fi
    if systemctl is-active --quiet syncthing@"$(whoami)" 2>/dev/null || systemctl --user is-active --quiet syncthing 2>/dev/null; then
        echo -e "${GREEN}✔ Syncthing service active${RESET}"
    else
        echo -e "${YELLOW}⚠ Syncthing service status unknown/inactive (checked systemd)${RESET}"
    fi
}

check_syncthing_remote() {
    HOST="$1"
    REMOTE_CMD="
        if systemctl is-active --quiet syncthing@\$(whoami) 2>/dev/null || systemctl --user is-active --quiet syncthing 2>/dev/null; then
            echo 'ACTIVE'
        else
            echo 'INACTIVE_OR_UNKNOWN'
        fi
    "
    OUTPUT=$(ssh -o ConnectTimeout=5 "$HOST" "$REMOTE_CMD" 2>&1)
    SSH_STATUS=$?

    if [ $SSH_STATUS -ne 0 ]; then
        echo -e "${RED}✘ SSH connection failed to $HOST${RESET}"
        return
    fi

    if echo "$OUTPUT" | grep -q "ACTIVE"; then
        echo -e "${GREEN}✔ Syncthing service active on $HOST${RESET}"
    else
        echo -e "${YELLOW}⚠ Syncthing service inactive/unknown on $HOST${RESET}"
    fi
}

FULL_OUTPUT_FILE=$(mktemp)

echo -e "${BOLD}NanoBot Health Check — $(date '+%Y-%m-%d %H:%M:%S')${RESET}" | tee -a "$FULL_OUTPUT_FILE"

{
section "Lenovo (local, controller)"
check_git_status_local
check_syncthing_local

section "Raspberry Pi 5 ($PI_HOST)"
check_git_status_remote "$PI_HOST"
check_syncthing_remote "$PI_HOST"

section "Jetson Orin Nano ($ORIN_HOST)"
check_git_status_remote "$ORIN_HOST"
check_syncthing_remote "$ORIN_HOST"
} | tee -a "$FULL_OUTPUT_FILE"

echo ""
echo -e "${BOLD}Health check complete.${RESET}"

if grep -q "MODIFIED TRACKED FILES" "$FULL_OUTPUT_FILE"; then
    echo ""
    echo -e "${RED}${BOLD}⚠⚠⚠  WARNING: One or more nodes have uncommitted changes to tracked files.  ⚠⚠⚠${RESET}"
    echo -e "${RED}Review and either commit or 'git restore' these before starting new work.${RESET}"
fi

rm -f "$FULL_OUTPUT_FILE"
