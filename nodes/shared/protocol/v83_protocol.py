# NanoBot v8.3 Protocol Definition
# Source of truth for controller ↔ Pi communication

from dataclasses import dataclass
from typing import Any, Dict, Optional
import uuid


# ----------------------------
# Message Types
# ----------------------------

MESSAGE_COMMAND = "command"
MESSAGE_ACK = "ack"
MESSAGE_RESULT = "result"
MESSAGE_HEARTBEAT = "heartbeat"


# ----------------------------
# Command Structure
# ----------------------------

def create_command(action: str, payload: Dict[str, Any], requires_ack: bool = True):
    return {
        "type": MESSAGE_COMMAND,
        "command_id": str(uuid.uuid4()),
        "action": action,
        "payload": payload,
        "requires_ack": requires_ack
    }


# ----------------------------
# ACK Messages
# ----------------------------

def create_ack(command_id: str, status: str = "received"):
    return {
        "type": MESSAGE_ACK,
        "command_id": command_id,
        "status": status
    }


# ----------------------------
# Result Messages
# ----------------------------

def create_result(command_id: str, status: str, output: Optional[Dict[str, Any]] = None):
    return {
        "type": MESSAGE_RESULT,
        "command_id": command_id,
        "status": status,
        "output": output or {}
    }


# ----------------------------
# Validation Helpers (lightweight v8.3)
# ----------------------------

def is_command(msg: Dict[str, Any]) -> bool:
    return msg.get("type") == MESSAGE_COMMAND


def is_ack(msg: Dict[str, Any]) -> bool:
    return msg.get("type") == MESSAGE_ACK


def is_result(msg: Dict[str, Any]) -> bool:
    return msg.get("type") == MESSAGE_RESULT
