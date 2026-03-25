"""
Airodor WiFi module emulator.

Emulates the HTTP API of a Limodor Airodor WiFi ventilation device so that the
Home Assistant integration can be tested without real hardware.

Device API format:  GET /msg?Function={action}{group}[{value}]

Actions:
  R{group}          - Read current mode  -> "R{group}{mode_number}"
  W{group}{mode}    - Write mode         -> "M{group}OK" / "M{group}NOOK"
  T{group}          - Read off-timer     -> "T{group}{hours}"
  S{group}{hours}   - Set off-timer      -> "S{group}OK" / "S{group}NOOK"

Usage:
  python3 scripts/airodor_emulator.py [--port 8866]
"""

from __future__ import annotations

import argparse
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [emulator] %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Device state (mutable at runtime)
# ---------------------------------------------------------------------------

# VentilationModeRead values used for the Read response
MODE_READ = {
    "OFF": 0,
    "ALTERNATING_MIN": 1,
    "ALTERNATING_MED": 2,
    "ALTERNATING_MED_FORCED": 3,
    "ALTERNATING_MAX": 6,
    "ONE_DIR_MED": 10,
    "ONE_DIR_MAX": 18,
    "INSIDE_MED": 34,
    "INSIDE_MAX": 66,
    "TIMED_OFF": 128,
}

# VentilationModeSet values expected in a Write command
MODE_SET = {
    0: 0,  # OFF -> read 0
    1: 1,  # ALTERNATING_MIN -> read 1
    2: 2,  # ALTERNATING_MED -> read 2
    4: 6,  # ALTERNATING_MAX -> read 6
    8: 10,  # ONE_DIR_MED -> read 10
    16: 18,  # ONE_DIR_MAX -> read 18
    32: 34,  # INSIDE_MED -> read 34
    64: 66,  # INSIDE_MAX -> read 66
}

state: dict[str, dict] = {
    "A": {"mode": MODE_READ["ALTERNATING_MED"], "timer": 0},
    "B": {"mode": MODE_READ["OFF"], "timer": 0},
}


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------


class AirodorHandler(BaseHTTPRequestHandler):
    """HTTP handler that implements the Airodor WiFi device protocol."""

    def log_message(self, fmt: str, *args: object) -> None:  # noqa: D102
        log.info(fmt, *args)

    def do_GET(self) -> None:
        """Dispatch an incoming GET request to the appropriate action handler."""
        parsed = urlparse(self.path)
        if parsed.path != "/msg":
            self._send(404, "Not Found")
            return

        params = parse_qs(parsed.query)
        func = params.get("Function", [None])[0]
        min_func_len = 2
        if func is None or len(func) < min_func_len:
            self._send(400, "Missing Function parameter")
            return

        action = func[0]
        group = func[1]

        if group not in ("A", "B"):
            self._send(400, f"Unknown group: {group}")
            return

        if action == "R":
            response = self._handle_read_mode(group)
        elif action == "W":
            response = self._handle_write_mode(group, func[2:])
        elif action == "T":
            response = self._handle_read_timer(group)
        elif action == "S":
            response = self._handle_set_timer(group, func[2:])
        else:
            self._send(400, f"Unknown action: {action}")
            return

        log.info("  <- %s", response)
        self._send(200, response)

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _handle_read_mode(self, group: str) -> str:
        mode = state[group]["mode"]
        log.info("READ mode group %s -> %d", group, mode)
        return f"R{group}{mode}"

    def _handle_write_mode(self, group: str, value_str: str) -> str:
        try:
            set_value = int(value_str)
        except ValueError:
            return f"M{group}NOOK"

        if set_value not in MODE_SET:
            log.warning("Unknown set-mode value %d for group %s", set_value, group)
            return f"M{group}NOOK"

        state[group]["mode"] = MODE_SET[set_value]
        state[group]["timer"] = 0
        log.info(
            "WRITE mode group %s = %d (read: %d)",
            group,
            set_value,
            state[group]["mode"],
        )
        return f"M{group}OK"

    def _handle_read_timer(self, group: str) -> str:
        timer = state[group]["timer"]
        log.info("READ timer group %s -> %d h", group, timer)
        return f"T{group}{timer}"

    def _handle_set_timer(self, group: str, value_str: str) -> str:
        try:
            hours = int(value_str)
        except ValueError:
            return f"S{group}NOOK"

        if hours <= 0:
            return f"S{group}NOOK"

        state[group]["timer"] = hours
        state[group]["mode"] = MODE_READ["TIMED_OFF"]
        log.info("SET timer group %s = %d h (mode -> TIMED_OFF)", group, hours)
        return f"S{group}OK"

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _send(self, code: int, body: str) -> None:
        encoded = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse CLI arguments and start the HTTP emulator server."""
    parser = argparse.ArgumentParser(description="Airodor WiFi emulator")
    parser.add_argument(
        "--port", type=int, default=8866, help="Port to listen on (default: 8866)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",  # noqa: S104
        help="Host to bind to (default: 0.0.0.0)",
    )
    args = parser.parse_args()

    log.info("Starting Airodor WiFi emulator on %s:%d", args.host, args.port)
    log.info("Initial state: Group A = %s, Group B = %s", state["A"], state["B"])
    log.info("Point your HA integration to: %s:%d", args.host, args.port)

    server = HTTPServer((args.host, args.port), AirodorHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Emulator stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
