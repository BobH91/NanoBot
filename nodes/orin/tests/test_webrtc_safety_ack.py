#!/usr/bin/env python3
"""Hardware-independent tests of Orin E-stop and scan acknowledgements."""

import ast
import asyncio
import json
import logging
import threading
from pathlib import Path
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1] / "webrtc_server.py"
tree = ast.parse(SOURCE.read_text())

wanted = {
    "estop_trigger", "estop_reset", "estop_is_active",
    "handle_command", "_send", "scan_start_handler",
}
functions = [
    node for node in tree.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    and node.name in wanted
]
assert {node.name for node in functions} == wanted

class Response:
    def __init__(self, payload, status):
        self.payload, self.status = payload, status

env = {
    "__builtins__": __builtins__,
    "json": json,
    "threading": threading,
    "logging": logging,
    "log": logging.getLogger("test"),
    "web": SimpleNamespace(
        Request=object,
        json_response=lambda payload, status=200: Response(payload, status),
    ),
    "_estop_active": False,
    "_estop_lock": threading.Lock(),
    "_motion_lock": threading.RLock(),
    "_scan_runner": None,
}
exec(compile(
    ast.fix_missing_locations(ast.Module(
        body=[ast.ImportFrom(
            module="__future__", names=[ast.alias(name="annotations")],
            level=0
        )] + functions,
        type_ignores=[],
    )),
    str(SOURCE), "exec",
), env)

class Client:
    def __init__(self, estop=True, stop=True):
        self.estop_result, self.stop_result = estop, stop
        self.estop_calls = self.stop_calls = 0

    def estop(self):
        self.estop_calls += 1
        return self.estop_result

    def stop(self):
        self.stop_calls += 1
        return self.stop_result

class Servos:
    def __init__(self):
        self.holds = 0

    def hold(self):
        self.holds += 1

class Runner:
    def __init__(self):
        self.estops = self.starts = 0

    def estop(self):
        self.estops += 1

    def start(self):
        self.starts += 1
        return True, "started"

class Channel:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(json.loads(message))

def reset():
    with env["_estop_lock"]:
        env["_estop_active"] = False
    env["_scan_runner"] = None

def test_estop_failure_latches():
    reset()
    client, servos, runner = Client(estop=False), Servos(), Runner()
    env.update(get_client=lambda: client, get_servos=lambda: servos,
               _scan_runner=runner)
    assert env["estop_trigger"]() is False
    assert env["estop_is_active"]()
    assert client.estop_calls == servos.holds == runner.estops == 1
    print("PASS: failed Pi E-stop acknowledgement preserves local latch")

def test_reset_failure_preserves_latch():
    reset()
    env["_estop_active"] = True
    client = Client(stop=False)
    env["get_client"] = lambda: client
    assert env["estop_reset"]() is False
    assert env["estop_is_active"]()
    print("PASS: failed reset acknowledgement preserves local latch")

def test_reset_success_clears_latch():
    reset()
    env["_estop_active"] = True
    env["get_client"] = lambda: Client(stop=True)
    assert env["estop_reset"]() is True
    assert not env["estop_is_active"]()
    print("PASS: acknowledged reset clears local latch")

def test_browser_event_reports_failed_ack():
    reset()
    client, servos, channel = Client(estop=False), Servos(), Channel()
    env.update(get_client=lambda: client, get_servos=lambda: servos)
    env["handle_command"]('{"cmd":"estop"}', channel)
    assert channel.messages == [{
        "event": "estop", "active": True, "pi_acknowledged": False
    }]
    print("PASS: browser event reports failed Pi acknowledgement")

def test_scan_refused_without_stop_ack():
    reset()
    client, runner = Client(stop=False), Runner()
    env["get_client"] = lambda: client
    request = SimpleNamespace(app={"scan_runner": runner})
    response = asyncio.run(env["scan_start_handler"](request))
    assert response.status == 503
    assert response.payload["ok"] is False
    assert runner.starts == 0
    print("PASS: scan refused when Pi does not acknowledge stop")

def test_scan_allowed_with_stop_ack():
    reset()
    client, runner = Client(stop=True), Runner()
    env["get_client"] = lambda: client
    request = SimpleNamespace(app={"scan_runner": runner})
    response = asyncio.run(env["scan_start_handler"](request))
    assert response.status == 200
    assert runner.starts == 1
    print("PASS: scan starts after acknowledged Pi stop")

if __name__ == "__main__":
    test_estop_failure_latches()
    test_reset_failure_preserves_latch()
    test_reset_success_clears_latch()
    test_browser_event_reports_failed_ack()
    test_scan_refused_without_stop_ack()
    test_scan_allowed_with_stop_ack()
    print("ALL PASS (6 tests)")
