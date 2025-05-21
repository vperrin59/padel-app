from scraper import get_matches2
from cache import MatchCache
from filter import filters
from notifier import send_notification

matches = get_matches2()

cache = MatchCache()

for match in matches:
    if all(f(match) for f in filters):
        # print(f"STABLE: {match.stable_hash()}")
        if not cache.has_seen(match):
            send_notification(match)
            # print(f"Notify {match}")
            cache.add(match)

cache.clear_expired()
cache.save()