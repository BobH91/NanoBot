#!/usr/bin/env python3
"""Hardware-independent tests for Pi command acknowledgements."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tcp_client import DriveClient


def client_with_response(response):
    client = DriveClient.__new__(DriveClient)
    client._send_recv = lambda _obj: response
    return client


def test_acknowledged_command():
    assert client_with_response({"status": "ok"})._send({"cmd": "stop"})
    print("PASS: acknowledged command returns True")


def test_rejected_command():
    assert not client_with_response({"status": "error"})._send({"cmd": "stop"})
    print("PASS: rejected command returns False")


def test_missing_response():
    assert not client_with_response(None)._send({"cmd": "estop"})
    print("PASS: missing response returns False")


if __name__ == "__main__":
    test_acknowledged_command()
    test_rejected_command()
    test_missing_response()
