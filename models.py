from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Optional, Iterator
from enum import IntEnum
import hashlib

DEFAULT_PLAYER_NAME = "libre"

@dataclass
class BasePlayer:
    name: str

    def is_empty(self) -> bool:
        # Treat empty or "libre" (free) players as empty
        return self.name.strip().lower() in ("", DEFAULT_PLAYER_NAME)

    def __str__(self):
        return f"{self.name}"

    def __hash__(self):
        return hash((self.name))

@dataclass
class Player(BasePlayer):
    level: float
    link: str
    position: str
    note: Optional[float] = None

    def __str__(self):
        return f"{self.name} ({self.level})"

    def __hash__(self):
        return hash((self.name))

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
    a_team: tuple[Player]
    b_team: tuple[Player]
    duration: int
    court: Optional[str] = None  # e.g. "Court 1", if available

    # Internal variable not passed in constructor (init=False)
    players_needed: int = field(init=False)
    min_level: float = field(init=False)
    max_level: float = field(init=False)

    @staticmethod
    def csv_header() -> tuple[str]:
        return ("date","court","player_a0","player_a1","player_b0","player_b1")

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

    def stable_hash(self) -> int:
        raw = f"{self.date.isoformat()}|{self.court}|{self.a_team[0].name}|{self.a_team[1].name}|{self.b_team[0].name}|{self.b_team[1].name}"
        digest = hashlib.sha256(raw.encode("utf-8")).digest()
        return int.from_bytes(digest[:8], byteorder='big', signed=False)

    def csv_row(self) -> tuple[str]:
        return (self.date.isoformat(),self.court,self.a_team[0].name,self.a_team[1].name,self.b_team[0].name,self.b_team[1].name)

    def __hash__(self):
        # Optional: allows using Match in a set for deduplication
        # return hash((self.date, self.location, self.level, self.a_team, self.b_team))
        return hash(self.date.isoformat() + self.location)

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

class UrbanCourt(IntEnum):
    COURT_1 = 1
    COURT_2 = 2
    COURT_3 = 3
    COURT_4 = 4

@dataclass
class UrbanMatch(Match):
    court: str

    duration: int = field(init=False)
    court_e: UrbanCourt = field(init=False)
    location: str = field(init="Lausanne")

    def parse_court(self, src: str) -> UrbanCourt:
        if src == "Terrain 1":
            return UrbanCourt.COURT_1
        elif src == "Terrain 2":
            return UrbanCourt.COURT_2
        elif src == "Terrain 3":
            return UrbanCourt.COURT_3
        elif src == "Terrain 4":
            return UrbanCourt.COURT_4
        else:
            assert 0

    def __post_init__(self):
        super().__post_init__()
        self.court_e = self.parse_court(self.court)
        if self.court_e in [UrbanCourt.COURT_2, UrbanCourt.COURT_4]:
            self.duration = 90
        else:
            self.duration = 60

    def __hash__(self):
        return super().__hash__()
