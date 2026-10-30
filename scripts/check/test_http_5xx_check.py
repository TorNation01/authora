#!/usr/bin/env python3
"""Self-test for http_5xx_check.py — the test that must fail before the fix.

Proves the checker's contract against real HTTP servers, not mocks of the checker:

  1. a live API returning 500/503 on real routes  -> checker exits 1, names them
  2. a healthy API (4xx allowed)                  -> checker exits 0
  3. a closed port                                -> checker exits 1 (unreachable)
  4. the old contract (reachability only)         -> exits 0 on (1)'s body, which
     is exactly the bug: the assertion below shows reachability alone is green.

Run:  python3 scripts/check/test_http_5xx_check.py
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

CHECK = Path(__file__).resolve().parent / "http_5xx_check.py"

SPEC = {
    "paths": {
        "/api/v1/books": {"get": {}},
        "/api/v1/projects": {"get": {}},
        "/api/v1/auth/me": {"get": {}},
        "/api/v1/books/{book_id}": {"get": {}},          # placeholder: must be skipped
        "/api/v1/accountability/cron/reminders": {"get": {}, "post": {}},  # denylisted
    }
}


class Handler(BaseHTTPRequestHandler):
    routes: dict[str, int] = {}

    def _send(self, code: int, body: bytes = b'{"status":"ok","app":"authora"}'):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/openapi.json":
            self._send(200, json.dumps(SPEC).encode())
            return
        if self.path in ("/health", "/health/ready", "/"):
            self._send(200)
            return
        self._send(self.routes.get(self.path, 404), b"{}")

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature
        pass

    def log_error(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature
        pass


def serve(routes: dict[str, int]) -> tuple[HTTPServer, str]:
    h = type("H", (Handler,), {"routes": routes})
    srv = HTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK), *args], capture_output=True, text=True, timeout=180
    )


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class FiveXXCheck(unittest.TestCase):
    BROKEN = {"/api/v1/books": 500, "/api/v1/projects": 503}
    HEALTHY = {"/api/v1/books": 401, "/api/v1/projects": 200, "/api/v1/auth/me": 403}

    def test_1_broken_api_fails_and_names_routes(self):
        srv, base = serve(self.BROKEN)
        try:
            r = run("--base-url", base)
        finally:
            srv.shutdown()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("500 /api/v1/books", r.stdout)
        self.assertIn("503 /api/v1/projects", r.stdout)
        self.assertIn("FAIL", r.stdout)

    def test_2_healthy_api_passes(self):
        srv, base = serve(self.HEALTHY)
        try:
            r = run("--base-url", base)
        finally:
            srv.shutdown()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_3_unreachable_fails(self):
        r = run("--base-url", f"http://127.0.0.1:{free_port()}", "--timeout", "2")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("UNREACHABLE", r.stdout)

    def test_4_discovery_skips_placeholders_and_side_effect_routes(self):
        srv, base = serve(self.HEALTHY)
        try:
            r = run("--base-url", base, "--json")
        finally:
            srv.shutdown()
        rep = json.loads(r.stdout)
        self.assertEqual(rep["probed"], 6, rep)  # health, ready, openapi, books, projects, auth/me
        dumped = json.dumps(rep)
        self.assertNotIn("books/{book_id}", dumped)      # path placeholder skipped
        self.assertNotIn("/cron/", dumped)               # side-effect route skipped
        self.assertEqual(rep["failures"], [])

    def test_5_old_contract_was_blind(self):
        """The bug itself: reachability-only passes on an API that 500s."""
        srv, base = serve(self.BROKEN)
        try:
            import urllib.request

            with urllib.request.urlopen(base + "/health", timeout=5) as ok:
                self.assertEqual(ok.status, 200)  # "reachable" -> old check green
        finally:
            srv.shutdown()


    def test_6_access_log_parser_counts_only_5xx(self):
        sys.path.insert(0, str(CHECK.parent))
        import http_5xx_check as c

        raw = (
            'INFO:  10.0.0.1:0 - "POST /api/v1/billing/webhooks/stripe HTTP/1.1" 500 Internal Server Error\n'
            'INFO:  127.0.0.1:0 - "POST /api/v1/billing/checkout/create HTTP/1.1" 503 Service Unavailable\n'
            'INFO:  127.0.0.1:0 - "GET /health HTTP/1.1" 200 OK\n'
            'INFO:  127.0.0.1:0 - "GET /api/v1/sagas HTTP/1.1" 401 Unauthorized\n'
            'audit_request status_code=401 path=/api/v1/sagas\n'
            'INFO:  127.0.0.1:0 - "GET /api/v1/books HTTP/1.1" 500 Internal Server Error\n'
        )
        hits = c.parse_5xx(raw)
        self.assertEqual(hits[("POST", "/api/v1/billing/webhooks/stripe", 500)], 1)
        self.assertEqual(hits[("POST", "/api/v1/billing/checkout/create", 503)], 1)
        self.assertEqual(hits[("GET", "/api/v1/books", 500)], 1)
        self.assertEqual(len(hits), 3)  # 200/401 lines ignored


if __name__ == "__main__":
    unittest.main(verbosity=2)
