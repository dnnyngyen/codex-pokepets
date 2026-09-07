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
    """A session's highest reached stage survives compaction and model changes."""

    def __init__(self, chain, thresholds=(33, 66)):
        if len(chain) != len(thresholds) + 1:
            raise ValueError("need one threshold for each evolution")
        if any(type(n) is not int or not 0 < n <= 100 for n in thresholds):
            raise ValueError("thresholds must be integers between 1 and 100")
        if any(a >= b for a, b in zip(thresholds, thresholds[1:])):
            raise ValueError("thresholds must be strictly increasing")
        self.chain = tuple(chain)
        self.thresholds = tuple(thresholds)
        self.stage = 0
        self.tokens = None
        self.window = None

    def consume(self, event):
        usage = context_usage(event)
        if usage is None:
            return
        self.tokens, self.window = usage
        reached = sum(self.tokens * 100 >= self.window * t for t in self.thresholds)
        self.stage = max(self.stage, reached)

    def snapshot(self):
        return {
            "slug": self.chain[self.stage],
            "stage": self.stage,
            "chain": self.chain,
            "thresholds": self.thresholds,
            "tokens": self.tokens,
            "window": self.window,
            "percent": None if self.tokens is None else min(100, self.tokens * 100 / self.window),
        }


class RolloutReader:
    """Read complete appended lines; retain partial records until their newline."""

    def __init__(self, path, evolution):
        self.path = Path(path)
        self.evolution = evolution
        self.offset = 0
        self.identity = None

    def poll(self):
        with self.path.open("rb") as stream:
            stat = os.fstat(stream.fileno())
            identity = (stat.st_dev, stat.st_ino)
            if identity != self.identity or stat.st_size < self.offset:
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
