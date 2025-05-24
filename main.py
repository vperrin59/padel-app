from scraper import get_matches2
from cache import MatchCache
from filter import filters
from notifier import send_notification
from models import Match

import csv

matches = get_matches2()

cache = MatchCache()

Match.csv_header()

with open("raw_matches.csv", mode="w", encoding="utf-8") as raw_f, \
     open("filtered_matches.csv", mode="w", encoding="utf-8") as filt_f:

    raw_writer = csv.writer(raw_f)
    filt_writer = csv.writer(filt_f)
    raw_writer.writerow(Match.csv_header())
    filt_writer.writerow(Match.csv_header())

    for match in matches:
        raw_writer.writerow(match.csv_row())
        if all(f(match) for f in filters):
            # Dump filtered matches
            filt_writer.writerow(match.csv_row())
            # print(f"STABLE: {match.stable_hash()}")
            if not cache.has_seen(match):
                send_notification(match)
                # print(f"Notify {match}")
                cache.add(match)

cache.clear_expired()
cache.save()