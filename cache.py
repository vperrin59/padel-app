import pickle
from datetime import datetime
from typing import Set

class MatchCache:
    """
    cache = {
        match_hash1: match_date1,
        match_hash2: match_date2,
        ...
    }
    """
    def __init__(self, path="seen_matches.pkl"):
        self.path = path
        try:
            with open(self.path, "rb") as f:
                self.seen: dict[int] = pickle.load(f)
        except FileNotFoundError:
            self.seen = dict()
        print(self.seen)

    def has_seen(self, match) -> bool:
        print(match.stable_hash())
        return match.stable_hash() in self.seen

    def add(self, match):
        sha = match.stable_hash()
        if sha in self.seen:
            assert 0
        else:
            self.seen[sha] = match.date

    def save(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.seen, f)

    def prune_cache(self, cache: dict) -> dict:
        now = datetime.now()
        # Keep only those whose match date is >= now (future or today)
        pruned_cache = {h: d for h, d in cache.items() if d >= now}
        return pruned_cache

    def clear_expired(self):
        self.seen = self.prune_cache(self.seen)
    
if __name__ == "__main__":
    cache = MatchCache()
