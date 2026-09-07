from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from evolution import Evolution, RolloutReader, resolve_chain
from test_evolution import token_event


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("companion", ROOT / "evolve-pet.py")
companion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(companion)


class SessionTests(unittest.TestCase):
    def test_explicit_path_and_missing_session(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            path.touch()
            self.assertEqual(companion.resolve_session(str(path)), path.resolve())
            with self.assertRaises(ValueError):
                companion.resolve_session(str(path) + ".missing")

    def test_uuid_respects_codex_home(self):
        with tempfile.TemporaryDirectory() as directory:
            session_id = "11111111-2222-3333-4444-555555555555"
            path = Path(directory) / "sessions" / "2026" / ("rollout-date-" + session_id + ".jsonl")
            path.parent.mkdir(parents=True)
            path.touch()
            with patch.dict("os.environ", {"CODEX_HOME": directory}):
                self.assertEqual(companion.resolve_session(session_id), path)


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "rollout.jsonl"
        self.path.write_text(json.dumps({"type": "response_item", "payload": {"text": "PRIVATE TRANSCRIPT"}}) + "\n")
        pet = Evolution(resolve_chain("charmander", "2d"))
        handler = companion.make_handler(RolloutReader(self.path, pet))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def get(self, path, headers=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.request("GET", path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_live_evolution_and_privacy(self):
        status, headers, body = self.get("/state.json")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertNotIn(b"PRIVATE TRANSCRIPT", body)
        self.assertIsNone(json.loads(body)["percent"])
        self.assertEqual(json.loads(body)["slug"], "charizard")
        for tokens, slug, in_ball in [(100, "charizard", False), (330, "charmeleon", False),
                                     (660, "charmander", False), (900, "charmander", True),
                                     (50, "charizard", False)]:
            with self.path.open("a") as stream:
                stream.write(json.dumps(token_event(tokens)) + "\n")
            state = json.loads(self.get("/state.json")[2])
            self.assertEqual(state["slug"], slug)
            self.assertEqual(state["tokens"], tokens)
            self.assertEqual(state["in_ball"], in_ball)
        self.path.unlink()
        state = json.loads(self.get("/state.json")[2])
        self.assertEqual(state["status"], "unavailable")
        self.assertEqual(state["slug"], "charizard")

    def test_assets_and_restricted_routes(self):
        self.assertEqual(self.get("/")[0], 200)
        status, headers, body = self.get("/pets/charmander.gif")
        self.assertEqual((status, headers["Content-Type"]), (200, "image/gif"))
        self.assertTrue(body.startswith(b"GIF"))
        status, headers, body = self.get("/pokeball.svg")
        self.assertEqual((status, headers["Content-Type"]), (200, "image/svg+xml"))
        self.assertIn(b"<svg", body)
        for path in ["/pets.json", "/pets/pikachu.gif", "/../README.md", "/%2e%2e/README.md", str(self.path)]:
            self.assertEqual(self.get(path)[0], 404)
        self.assertEqual(self.get("/state.json", {"Host": "attacker.example"})[0], 403)


if __name__ == "__main__":
    unittest.main()
