import json
from pathlib import Path
import tempfile
import unittest

from evolution import CHAINS, Evolution, RolloutReader, context_usage, resolve_chain


def token_event(tokens, window=1000):
    """Build a usage snapshot with a misleading cumulative counter to detect overcounting."""
    return {"type": "event_msg", "payload": {"type": "token_count", "info": {
        "last_token_usage": {"total_tokens": tokens},
        "total_token_usage": {"total_tokens": 999999999},
        "model_context_window": window,
    }}}


class EvolutionTests(unittest.TestCase):
    def test_boundaries_and_compaction(self):
        """Exact thresholds change forms in both directions as current usage rises or falls."""
        pet = Evolution(resolve_chain("charmander", "2d"))
        self.assertEqual(pet.snapshot()["slug"], "charizard")
        for tokens, expected, in_ball in [(0, 2, False), (329, 2, False), (330, 1, False),
                                         (659, 1, False), (660, 0, False), (899, 0, False),
                                         (900, 0, True), (950, 0, True), (1000, 0, True),
                                         (899, 0, False), (659, 1, False), (50, 2, False)]:
            pet.consume(token_event(tokens))
            self.assertEqual(pet.stage, expected)
            self.assertEqual(pet.snapshot()["in_ball"], in_ball)
        self.assertEqual(pet.snapshot()["percent"], 5)

    def test_duplicates_do_not_accumulate(self):
        """Repeated snapshots must not advance degradation through cumulative counting."""
        pet = Evolution(resolve_chain("bulbasaur", "2d"))
        for _ in range(10):
            pet.consume(token_event(200))
        self.assertEqual(pet.stage, 2)

    def test_model_window_and_overflow(self):
        """Use the current model window and cap usage when it exceeds capacity."""
        pet = Evolution(resolve_chain("squirtle", "3d"))
        pet.consume(token_event(330, 2000))
        self.assertEqual(pet.stage, 2)
        pet.consume(token_event(330, 1000))
        self.assertEqual(pet.snapshot()["slug"], "wartortle-3d")
        pet.consume(token_event(2000, 1000))
        self.assertEqual(pet.snapshot()["percent"], 100)
        self.assertEqual(pet.stage, 0)
        self.assertTrue(pet.in_ball)
        pet.consume(token_event(2000, 10000))
        self.assertEqual(pet.snapshot()["slug"], "blastoise-3d")
        self.assertFalse(pet.in_ball)

    def test_missing_or_invalid_telemetry(self):
        """Ignore unrelated, absent, and malformed usage without inventing a percentage."""
        for event in [None, [], {}, {"type": "event_msg", "payload": []},
                      {"type": "event_msg", "payload": {"type": "token_count", "info": None}}]:
            self.assertIsNone(context_usage(event))
        for tokens, window in [(1, 0), (-1, 100), (1, None), (True, 100), (1, False),
                               ("330", 1000), (float("nan"), 1000)]:
            self.assertIsNone(context_usage(token_event(tokens, window)))
        self.assertIsNone(Evolution(resolve_chain("charmander", "2d")).snapshot()["percent"])

    def test_large_integer_percentages(self):
        """Large valid counts stay bounded without overflowing float conversion."""
        pet = Evolution(resolve_chain("charmander", "2d"))
        for tokens, window, expected in [(10**1000, 1, 100),
                                         (10**1000, 10**1000, 100),
                                         (10**1000, 10**1001, 10),
                                         (0, 10**1000, 0)]:
            with self.subTest(window_digits=len(str(window)), expected=expected):
                pet.consume(token_event(tokens, window))
                self.assertEqual(pet.snapshot()["percent"], expected)

    def test_threshold_validation(self):
        """Reject invalid degradation ranges while honoring custom boundaries."""
        for thresholds in [(66, 33), (33, 33), (0, 66), (33, 101), (33,), (True, 66)]:
            with self.assertRaises(ValueError):
                Evolution(resolve_chain("charmander", "2d"), thresholds)
        pet = Evolution(resolve_chain("charmander", "2d"), (25, 75))
        pet.consume(token_event(250))
        self.assertEqual(pet.stage, 1)

    def test_custom_ball_threshold(self):
        """Enter at a custom ball boundary and recover only after actual usage decreases."""
        for threshold in [0, 66, 101, True, 90.5]:
            with self.assertRaises(ValueError):
                Evolution(resolve_chain("charmander", "2d"), ball_at=threshold)
        pet = Evolution(resolve_chain("charmander", "2d"), ball_at=95)
        pet.consume(token_event(949))
        self.assertFalse(pet.in_ball)
        pet.consume(token_event(950))
        self.assertTrue(pet.in_ball)
        pet.consume({"type": "event_msg", "payload": {"type": "context_compacted"}})
        # Wait for actual usage instead of assuming compaction freed the entire window.
        self.assertTrue(pet.in_ball)
        pet.consume(token_event(100))
        self.assertFalse(pet.in_ball)
        self.assertEqual(pet.stage, 2)

    def test_every_builtin_chain_has_assets(self):
        """Every supported style and family must reference an existing matching pet atlas."""
        root = Path(__file__).resolve().parents[1]
        for starter in CHAINS:
            for style in ("2d", "3d"):
                for slug in resolve_chain(starter, style):
                    folder = root / "pets" / slug
                    manifest = json.loads((folder / "pet.json").read_text())
                    self.assertEqual(manifest["id"], slug)
                    self.assertTrue((folder / manifest["spritesheetPath"]).is_file())

    def test_sessions_are_independent(self):
        """Usage in one session must not affect another session's form."""
        first = Evolution(resolve_chain("charmander", "2d"))
        second = Evolution(resolve_chain("charmander", "2d"))
        first.consume(token_event(700))
        second.consume(token_event(100))
        self.assertEqual((first.stage, second.stage), (0, 2))


class ReaderTests(unittest.TestCase):
    def test_partial_appends_malformed_lines_and_resume(self):
        """Defer partial records, skip bad lines, and restore the latest state on replay."""
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
            self.assertEqual(pet.stage, 2)
            with path.open("ab") as stream:
                stream.write(record[40:] + b"\n")
            reader.poll()
            self.assertEqual(pet.stage, 0)
            offset = reader.offset
            reader.poll()
            self.assertEqual(reader.offset, offset)
            # Restarting uses the latest usage, including recovery after compaction.
            with path.open("a") as stream:
                stream.write(json.dumps(token_event(950)) + "\n")
                stream.write(json.dumps(token_event(100)) + "\n")
            resumed = Evolution(resolve_chain("charmander", "2d"))
            RolloutReader(path, resumed).poll()
            self.assertEqual(resumed.stage, 2)
            self.assertFalse(resumed.in_ball)

    def test_truncation_and_replacement(self):
        """Reset stale usage when the rollout is truncated, replaced, or emptied."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            path.write_text(json.dumps(token_event(400)) + "\n" + "{}\n" * 100)
            pet = Evolution(resolve_chain("charmander", "2d"))
            reader = RolloutReader(path, pet)
            reader.poll()
            path.write_text(json.dumps(token_event(700)) + "\n")
            reader.poll()
            self.assertEqual(pet.stage, 0)
            replacement = path.with_suffix(".new")
            replacement.write_text(json.dumps(token_event(100)) + "\n")
            replacement.replace(path)
            reader.poll()
            self.assertEqual(pet.tokens, 100)
            self.assertEqual(pet.stage, 2)
            path.write_text("")
            reader.poll()
            self.assertIsNone(pet.tokens)
            self.assertEqual(pet.stage, 2)


if __name__ == "__main__":
    unittest.main()
