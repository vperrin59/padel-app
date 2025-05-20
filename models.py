from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Optional, Iterator

DEFAULT_PLAYER_NAME = "libre"

@dataclass
class BasePlayer:
    name: str

    def is_empty(self) -> bool:
        # Treat empty or "libre" (free) players as empty
        return self.name.strip().lower() in ("", DEFAULT_PLAYER_NAME)

    def __str__(self):
        return f"{self.name}"

@dataclass
class Player(BasePlayer):
    level: float
    link: str
    position: str

    def __str__(self):
        return f"{self.name} ({self.level})"

EmptyPlayer = BasePlayer(name=DEFAULT_PLAYER_NAME)

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
            1 for p in self.a_team + self.b_team if p.is_empty()
        )
        self.min_level = self.level - 1
        self.max_level = self.level + 1

    def active_players(self) -> Iterator[Player]:
        for player in self.a_team + self.b_team:
            if not player.is_empty():
                yield player

    def __hash__(self):
        # Optional: allows using Match in a set for deduplication
        return hash((self.date, self.location, self.level, self.a_team, self.b_team))

    def __str__(self):
        a_team_str = "A: "
        b_team_str = "B:"
        for p in self.a_team:
            a_team_str += str(p)
            a_team_str += "-"
        for p in self.b_team:
            b_team_str += str(p)
            b_team_str += "-"
        return f"[{self.date.strftime('%Y-%m-%d %H:%M')}] {self.court} ({self.level}), needs {self.players_needed}" + f"\n{a_team_str}" + f"\n{b_team_str}"
