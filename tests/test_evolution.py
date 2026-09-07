import json
from pathlib import Path
import tempfile
import unittest

from evolution import CHAINS, Evolution, RolloutReader, context_usage, resolve_chain


def token_event(tokens, window=1000):
    return {"type": "event_msg", "payload": {"type": "token_count", "info": {
        "last_token_usage": {"total_tokens": tokens},
        "total_token_usage": {"total_tokens": 999999999},
        "model_context_window": window,
    }}}


class EvolutionTests(unittest.TestCase):
    def test_boundaries_and_compaction(self):
        pet = Evolution(resolve_chain("charmander", "2d"))
        for tokens, expected in [(0, 0), (329, 0), (330, 1), (659, 1), (660, 2), (50, 2)]:
            pet.consume(token_event(tokens))
            self.assertEqual(pet.stage, expected)
        self.assertEqual(pet.snapshot()["percent"], 5)

    def test_duplicates_do_not_accumulate(self):
        pet = Evolution(resolve_chain("bulbasaur", "2d"))
        for _ in range(10):
            pet.consume(token_event(200))
        self.assertEqual(pet.stage, 0)

    def test_model_window_and_overflow(self):
        pet = Evolution(resolve_chain("squirtle", "3d"))
        pet.consume(token_event(330, 2000))
        self.assertEqual(pet.stage, 0)
        pet.consume(token_event(330, 1000))
        self.assertEqual(pet.snapshot()["slug"], "wartortle-3d")
        pet.consume(token_event(2000, 1000))
        self.assertEqual(pet.snapshot()["percent"], 100)
        self.assertEqual(pet.stage, 2)

    def test_missing_or_invalid_telemetry(self):
        for event in [None, [], {}, {"type": "event_msg", "payload": []},
                      {"type": "event_msg", "payload": {"type": "token_count", "info": None}}]:
            self.assertIsNone(context_usage(event))
        for tokens, window in [(1, 0), (-1, 100), (1, None), (True, 100), (1, False),
                               ("330", 1000), (float("nan"), 1000)]:
            self.assertIsNone(context_usage(token_event(tokens, window)))
        self.assertIsNone(Evolution(resolve_chain("charmander", "2d")).snapshot()["percent"])

    def test_threshold_validation(self):
        for thresholds in [(66, 33), (33, 33), (0, 66), (33, 101), (33,), (True, 66)]:
            with self.assertRaises(ValueError):
                Evolution(resolve_chain("charmander", "2d"), thresholds)
        pet = Evolution(resolve_chain("charmander", "2d"), (25, 75))
        pet.consume(token_event(250))
        self.assertEqual(pet.stage, 1)

    def test_every_builtin_chain_has_assets(self):
        root = Path(__file__).resolve().parents[1]
        for starter in CHAINS:
            for style in ("2d", "3d"):
                for slug in resolve_chain(starter, style):
                    folder = root / "pets" / slug
                    manifest = json.loads((folder / "pet.json").read_text())
                    self.assertEqual(manifest["id"], slug)
                    self.assertTrue((folder / manifest["spritesheetPath"]).is_file())

    def test_sessions_are_independent(self):
        first = Evolution(resolve_chain("charmander", "2d"))
        second = Evolution(resolve_chain("charmander", "2d"))
        first.consume(token_event(700))
        second.consume(token_event(100))
        self.assertEqual((first.stage, second.stage), (2, 0))


class ReaderTests(unittest.TestCase):
    def test_partial_appends_malformed_lines_and_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            path.write_bytes(b'not json\n{"type":"response_item"}\n')
            pet = Evolution(resolve_chain("charmander", "2d"))
            reader = RolloutReader(path, pet)
            reader.poll()
            record = json.dumps(token_event(660)).encode()
            with path.open("ab") as stream:
                stream.write(record[:40])
            reader.poll()
            self.assertEqual(pet.stage, 0)
            with path.open("ab") as stream:
                stream.write(record[40:] + b"\n")
            reader.poll()
            self.assertEqual(pet.stage, 2)
            offset = reader.offset
            reader.poll()
            self.assertEqual(reader.offset, offset)
            # Restarting replays history, preserving evolution without a state file.
            resumed = Evolution(resolve_chain("charmander", "2d"))
            RolloutReader(path, resumed).poll()
            self.assertEqual(resumed.stage, 2)

    def test_truncation_and_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            path.write_text(json.dumps(token_event(400)) + "\n" + "{}\n" * 100)
            pet = Evolution(resolve_chain("charmander", "2d"))
            reader = RolloutReader(path, pet)
            reader.poll()
            path.write_text(json.dumps(token_event(700)) + "\n")
            reader.poll()
            self.assertEqual(pet.stage, 2)
            replacement = path.with_suffix(".new")
            replacement.write_text(json.dumps(token_event(100)) + "\n")
            replacement.replace(path)
            reader.poll()
            self.assertEqual(pet.tokens, 100)
            self.assertEqual(pet.stage, 2)


if __name__ == "__main__":
    unittest.main()
