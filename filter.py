from typing import Optional, Iterator
from models import Match
from config import *
from datetime import datetime

from scraper import get_matches2

class BaseMatchFilter:

    def __call__(self, match: Match) -> bool:
        print("base match filter class")
        raise NotImplementedError

class MatchOpenFilter(BaseMatchFilter):

    def __call__(self, match: Match) -> bool:
        return 0 < match.players_needed < 4

class MatchFutureFilter(BaseMatchFilter):

    def __call__(self, match: Match) -> bool:
        return match.date >= datetime.now()

class MatchDurationFilter(BaseMatchFilter):
    def __init__(self, duration: int):
        self.duration = duration

    def __call__(self, match: Match) -> bool:
        return match.duration == self.duration

class MatchMyLevelFilter(BaseMatchFilter):
    def __init__(self, my_level: float):
        self.my_level = my_level

    def __call__(self, match: Match) -> bool:
        # Filter by number of players needed
        if match.min_level <= self.my_level <= match.max_level:
            return True
        else:
            return False

class MatchPartnerLevelFilter(BaseMatchFilter):
    def __init__(self, level: float):
        self.min_level = level

    def __call__(self, match: Match) -> bool:
        for p in match.active_players():
            if p.level:
                if p.level <= self.min_level:
                    return False
        return True

class MatchPartnerNameFilter(BaseMatchFilter):
    def __init__(self, player_names: list[str]):
        self.player_names = player_names

    def __call__(self, match: Match) -> bool:
        for p in match.active_players():
            if p.name.lower() in self.player_names:
                return False
        return True

if __name__ == "__main__":
    filters: list[BaseMatchFilter] = [
        MatchOpenFilter(),
        MatchFutureFilter(),
        MatchDurationFilter(duration=90),
        MatchMyLevelFilter(my_level=MY_LEVEL),
        MatchPartnerLevelFilter(level=MIN_PARTNER_LEVEL),
    ]

    matches = get_matches2()

    for match in matches:
        if all(f(match) for f in filters):
            print(match)