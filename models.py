from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Optional

@dataclass
class BasePlayer:
    name: str

    def is_empty(self) -> bool:
        # Treat empty or "libre" (free) players as empty
        return self.name.strip().lower() in ("", "libre")

@dataclass
class Player(BasePlayer):
    level: float
    link: str
    position: str

EmptyPlayer = BasePlayer(name="Libre")

@dataclass
class Match:
    """
        We should add criteria related to match level and my level
        We should add criteria related to player names
        We should add criteria related to player levels
    """

    date: datetime          # Full date and time of the match
    location: str           # e.g. "Lausanne - Padel Club"
    level: str              # e.g. "Intermediate", "Advanced"
    match_type: str         # e.g. "Mixte", "Tournoi", "Privé"
    a_team: list[Player]
    b_team: list[Player]
    court: Optional[str] = None  # e.g. "Court 1", if available

    # Internal variable not passed in constructor (init=False)
    players_needed: int = field(init=False)
    min_level: float = field(init=False)
    max_level: float = field(init=False)

    def __post_init__(self):
        # Compute the winner right after init
        self.players_needed = sum(
            1 for p in self.a_team + self.b_team if p.name.lower() == "libre"
        )
        self.min_level = self.level - 1
        self.max_level = self.level + 1

    def matches_criteria(self, criteria: dict) -> bool:
        """Custom match filtering based on a criteria dict."""
        if 'location' in criteria and self.location != criteria['location']:
            return False
        if 'level' in criteria and self.level not in criteria['level']:
            return False
        if 'after' in criteria and self.date.time() < criteria['after']:
            return False
        if 'before' in criteria and self.date.time() > criteria['before']:
            return False
        if 'players_needed' in criteria and self.players_needed > criteria['players_needed']:
            return False
        return True

    def matches_players_level_criteria(self, min_players_level: float) -> bool:
        """ Minimum level for all active players"""
        res = True
        for p in (a_team + b_team):
            if not p.is_empty():
                if p.level:
                    if p.level <= min_players_level:
                        return False

    def __hash__(self):
        # Optional: allows using Match in a set for deduplication
        return hash((self.date, self.location, self.level, self.a_team, self.b_team))

    def __str__(self):
        return f"[{self.date.strftime('%Y-%m-%d %H:%M')}] {self.location} ({self.level}) - {self.match_type}, needs {self.players_needed}"
