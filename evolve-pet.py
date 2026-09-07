#!/usr/bin/env python3
"""Show a local Pokémon companion that evolves with a Codex session's context."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import sys
import threading

from evolution import CHAINS, Evolution, RolloutReader, resolve_chain


ROOT = Path(__file__).resolve().parent


def resolve_session(value):
    path = Path(value).expanduser()
    if path.is_file():
        return path.resolve()
    if re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", value):
        codex_dir = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
        matches = list((codex_dir / "sessions").rglob("rollout-*-" + value.lower() + ".jsonl"))
        if len(matches) == 1:
            return matches[0]
    raise ValueError("session not found; pass an existing rollout JSONL path or session UUID")


def make_handler(reader):
    chain = reader.evolution.chain
    lock = threading.Lock()
    names = {
        slug: json.loads((ROOT / "pets" / slug / "pet.json").read_text())["displayName"]
        for slug in chain
    }
    assets = {"/pets/" + slug + ".gif": ROOT / "pets" / slug / "preview.gif" for slug in chain}
    for path in assets.values():
        if not path.is_file():
            raise ValueError("missing pet preview: " + str(path))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, body, content_type, status=200):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            # Bind to loopback and reject DNS-rebinding hosts. No session text is served.
            expected_host = "127.0.0.1:" + str(self.server.server_port)
            if self.headers.get("Host") != expected_host:
                self.respond(b"Invalid host", "text/plain", 403)
                return
            if self.path == "/":
                self.respond((ROOT / "assets" / "evolution.html").read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/state.json":
                status = "watching"
                with lock:
                    try:
                        reader.poll()
                    except OSError:
                        status = "unavailable"
                    state = reader.evolution.snapshot()
                state.update(names=names, status=status)
                self.respond(json.dumps(state).encode(), "application/json")
            elif self.path in assets:
                self.respond(assets[self.path].read_bytes(), "image/gif")
            elif self.path == "/favicon.ico":
                self.respond(b"", "image/x-icon", 204)
            else:
                self.respond(b"Not found", "text/plain", 404)

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("starter", nargs="?", choices=sorted(CHAINS), default="charmander")
    parser.add_argument("--session", required=True, help="rollout JSONL path or Codex session UUID")
    parser.add_argument("--style", choices=("2d", "3d"), default="2d")
    parser.add_argument("--thresholds", nargs=2, type=int, default=(33, 66), metavar=("FIRST", "FINAL"),
                        help="context percentages at which to evolve (default: 33 66)")
    parser.add_argument("--port", type=int, default=0, help="local port (default: choose a free port)")
    args = parser.parse_args()
    try:
        if not 0 <= args.port <= 65535:
            raise ValueError("port must be between 0 and 65535")
        pet = Evolution(resolve_chain(args.starter, args.style), args.thresholds)
        reader = RolloutReader(resolve_session(args.session), pet)
        reader.poll()
        handler = make_handler(reader)
        with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
            print("Watching: " + str(reader.path), flush=True)
            print("Open http://127.0.0.1:" + str(server.server_port) + "/", flush=True)
            print("Keep this terminal open. Press Ctrl+C to stop.", flush=True)
            server.serve_forever()
    except (OSError, ValueError) as error:
        parser.exit(1, "Error: " + str(error) + "\n")
    except KeyboardInterrupt:
        print("\nCompanion stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
