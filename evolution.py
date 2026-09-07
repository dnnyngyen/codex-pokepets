"""Context-driven evolution policy and incremental Codex rollout reader."""

import json
import os
from pathlib import Path


CHAINS = {
    "bulbasaur": ("bulbasaur", "ivysaur", "venusaur"),
    "charmander": ("charmander", "charmeleon", "charizard"),
    "squirtle": ("squirtle", "wartortle", "blastoise"),
}


def resolve_chain(starter, style):
    """Return the family in earliest-to-final order using the requested sprite style."""
    suffix = "-3d" if style == "3d" else ""
    return tuple(species + suffix for species in CHAINS[starter])


def context_usage(event):
    """Return the latest request's (tokens, window), never cumulative usage."""
    if not isinstance(event, dict) or event.get("type") != "event_msg":
        return None
    payload = event.get("payload")
    if not isinstance(payload, dict) or payload.get("type") != "token_count":
        return None
    info = payload.get("info")
    if not isinstance(info, dict):
        return None
    usage = info.get("last_token_usage")
    if not isinstance(usage, dict):
        return None
    tokens, window = usage.get("total_tokens"), info.get("model_context_window")
    if type(tokens) is not int or type(window) is not int:
        return None
    if tokens < 0 or window <= 0:
        return None
    return tokens, window


class Evolution:
    """Current context pressure determines form; compaction restores stronger forms."""

    def __init__(self, chain, thresholds=(33, 66), ball_at=90):
        """Validate ordered thresholds and initialize a fully evolved, unmeasured pet."""
        if not thresholds or len(chain) != len(thresholds) + 1:
            raise ValueError("need one threshold for each evolution")
        if any(type(n) is not int or not 0 < n <= 100 for n in thresholds):
            raise ValueError("thresholds must be integers between 1 and 100")
        if any(a >= b for a, b in zip(thresholds, thresholds[1:])):
            raise ValueError("thresholds must be strictly increasing")
        if type(ball_at) is not int or not thresholds[-1] < ball_at <= 100:
            raise ValueError("Poké Ball threshold must exceed degradation thresholds and be at most 100")
        self.chain = tuple(chain)
        self.thresholds = tuple(thresholds)
        self.ball_at = ball_at
        self.reset()

    def reset(self):
        """Clear usage when beginning or replaying a rollout."""
        self.stage = len(self.chain) - 1
        self.in_ball = False
        self.tokens = None
        self.window = None

    def consume(self, event):
        """Apply a valid usage snapshot; leave state unchanged for unrelated records."""
        usage = context_usage(event)
        if usage is None:
            return
        self.tokens, self.window = usage
        pressure = sum(self.tokens * 100 >= self.window * t for t in self.thresholds)
        self.stage = len(self.chain) - 1 - pressure
        self.in_ball = self.tokens * 100 >= self.window * self.ball_at

    def snapshot(self):
        """Return display state with an unknown or safely bounded usage percentage."""
        return {
            "slug": self.chain[self.stage],
            "stage": self.stage,
            "chain": self.chain,
            "thresholds": self.thresholds,
            "ball_at": self.ball_at,
            "in_ball": self.in_ball,
            "tokens": self.tokens,
            "window": self.window,
            "percent": (
                None if self.tokens is None
                else 100 if self.tokens >= self.window
                else self.tokens / self.window * 100
            ),
        }


class RolloutReader:
    """Read complete appended lines; retain partial records until their newline."""

    def __init__(self, path, evolution):
        """Track the selected file and its last complete record offset."""
        self.path = Path(path)
        self.evolution = evolution
        self.offset = 0
        self.identity = None

    def poll(self):
        """Consume appended records, replay changed files, and defer incomplete lines."""
        with self.path.open("rb") as stream:
            stat = os.fstat(stream.fileno())
            identity = (stat.st_dev, stat.st_ino)
            if identity != self.identity or stat.st_size < self.offset:
                self.evolution.reset()
                self.offset = 0
                self.identity = identity
            stream.seek(self.offset)
            while True:
                line = stream.readline()
                if not line.endswith(b"\n"):
                    break
                self.offset = stream.tell()
                try:
                    event = json.loads(line)
                except (ValueError, UnicodeDecodeError):
                    continue
                self.evolution.consume(event)
