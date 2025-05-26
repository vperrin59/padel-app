import requests
from bs4 import BeautifulSoup
import re
from config import *
from models import Player, Match, EmptyPlayer, UrbanCourt, UrbanMatch
import traceback
import unicodedata

from datetime import date, datetime, time, timedelta
from typing import Optional, ClassVar
from dataclasses import dataclass

@dataclass
class ScrapePlayer(Player):

    scraped_players: ClassVar[dict[str, float]] = {}

    def register_player(self):
        ScrapePlayer.scraped_players[self.name] = self.level

    def upd_from_url(self):
        if self.name in ScrapePlayer.scraped_players:
            self.level = ScrapePlayer.scraped_players[self.name]
        else:
            url = urban_link_prefix + self.link
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            self.level = parse_player_level(soup.find("span", id=re.compile(r".*ctl00_WUCRegistroNivelJuego_LabelValorNivel$")).text.strip())
            note = soup.find("span", id=re.compile(r".*_LabelValorPuntuacionRanking$"))
            if note:
                self.note = parse_player_level(note.text.strip())
            else:
                self.note = 0.0
            self.register_player()
            
    def __hash__(self):
        return super().__hash__()

def get_page_html() -> str:
    """Fetch the HTML of the match page."""
    response = requests.get(URL)
    response.raise_for_status()
    return response.text

def get_page_html2(date: datetime.date) -> str:
    """Fetch the HTML of the match page."""
    response = requests.get(urban_link_prefix + f"Grid.aspx?f={date.strftime('%d/%m/%Y')}&c=3")
    response.raise_for_status()
    return response.text

def parse_match_element(el: str) -> Match:
    """Parse a single HTML block into a Match object."""
    # print(el)
    day_pat_re = re.compile(r'.*LabelDiaSemana$')
    day = el.find("span", id=day_pat_re).text.strip()
    time_pat_re = re.compile(r'.*LabelHoraInicio$')
    start_time = el.find("span", id=time_pat_re).text.strip()
    level_pat_re = re.compile(r'.*LabelNivelValor$')
    level = el.find("span", id=level_pat_re).text.strip()
    (min_level, max_level) = level.split(" - ")
    match_url = el.find("a", class_='boton')["href"]

    return Match(
        date=datetime.now(),
        location="Lausanne",
        level=level,
        match_type="Toto",
    )

def clean_string(s: str) -> str:
    # Normalize accented characters (é -> e, ñ -> n, etc.)
    s = unicodedata.normalize('NFD', s)
    s = s.encode('ascii', 'ignore').decode('utf-8')

    # Remove all characters except letters, digits, commas, spaces, dash, and parentheses
    s = re.sub(r'[^a-zA-Z0-9,\s\-\(\)]', '', s)

    # Collapse multiple spaces (optional)
    s = re.sub(r'\s+', ' ', s)

    return s.strip()

def parse_player_info(player_str: str) -> dict:
    # Improved regex pattern:
    # Optional level like "0,66-", captured as "level"
    # Name allows letters, accents, spaces, hyphens
    # Position is inside parentheses
    pattern = r'^(?:(?P<level>[\d,]+)-)?(?P<name>[^()]+?)(?:\s*\((?P<position>[^()]+)\))?$'
    match = re.match(pattern, player_str.strip(), re.UNICODE)
    
    if (not match) or (match.group("name").strip().lower() == "libre"):
        # print(player_str)
        raise ValueError(f"Invalid player format: {player_str}")
    
    return {
        "level": match.group("level"),
        "name": match.group("name").strip(),
        "position": match.group("position")
    }

def parse_match_level(level_str: str) -> float:
    """
        Possible formats:
        * Niveaux: 0,10 - 2,02
        * Tous les niveaux
    """
    match = re.search(r"Niveaux:\s*([\d,]+)\s*-\s*([\d,]+)", level_str)

    if match:
        min_level_str, max_level_str = match.groups()
        # Replace ',' with '.' to convert to float properly
        min_level = float(min_level_str.replace(',', '.'))
        max_level = float(max_level_str.replace(',', '.'))
        # print(f"Min level: {min_level}, Max level: {max_level}")
    elif level_str == "Tous les niveaux":
        # This is a rare case for full match usually
        # when people of different level wanted to play together
        min_level = 0
        max_level = 0
    else:
        print(level_str)
        print("No levels found")

    return (min_level, max_level)

def parse_player_level(level_str: str) -> float:
    return float(level_str.replace(',', '.'))

def fetch_player_level(url: str) -> float:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    level = soup.find("span", id=re.compile(r".*ctl00_WUCRegistroNivelJuego_LabelValorNivel$")).text.strip()
    note = soup.find("span", id=re.compile(r".*_LabelValorPuntuacionRanking$"))
    if note:
        note = note.text.strip()
    else:
        note = "0.0"
    print(level)
    print(note)

def parse_match_element2(el: str) -> UrbanMatch:
    """
        Parse a single HTML block into a UrbanMatch object.
        First div is the URL link
        Then we need to parse players in the next sibling div
    """
    """ Don't parse hidden games"""

    # Regex to identify the match link inside gridviewestilocabecera div
    match_link_id_re = re.compile(r'_HyperLinkHorario$')
    # Find the <a> inside this div with id matching pattern
    a_tag = el.find("a", id=match_link_id_re)

    if not a_tag:
        return None

    match_url = a_tag.get("href")
    match_text = a_tag.text.strip()
    
    # print(match_url)
    # print(match_text)

    player_match_el = el.find_next_sibling("div")

    # day_pat_re = re.compile(r'.*LabelDiaSemana$')
    # day = el.find("span", id=day_pat_re).text.strip()
    # time_pat_re = re.compile(r'.*LabelHoraInicio$')
    # start_time = el.find("span", id=time_pat_re).text.strip()
    level_pat_re = re.compile(r'.*LabelDescripcionNiveles$')
    level = player_match_el.find("span", id=level_pat_re).text.strip()
    if level:
        # print(player_match_el)
        # print(level)
        (min_level, max_level) = parse_match_level(level)
        status_pat_re = re.compile(r'.*ElementoPartidaCuadro_LabelEstado$')
        status = player_match_el.find("span", id=status_pat_re).text.strip()
        # print(status)
        # match_url_pat_re = re.compile(r'.*DataListPartidas_ctl03_WUCElementoPartidaCuadro_HyperLinkHorario$')
        # match_url = player_match_el.find("a", id=match_url_pat_re)
        # print(match_url)
        court = match_text[:9].strip()
        start_time = match_text[9:].strip()
        players = []

        for pat in ["EquipoA_ctl00", "EquipoA_ctl01", "EquipoB_ctl00", "EquipoB_ctl01"]:
            player_pat_re = re.compile(f".*{pat}_WUCParticipantePartidaCuadro_LabelTexto$")
            try:
                player = player_match_el.find("span", id=player_pat_re).text.strip()
                # print(f"{pat}: {player}")
                # print(player)
                player = clean_string(player)
                # print(player)
                player_info = parse_player_info(player)
                link_player_pat_re = re.compile(f".*{pat}_WUCParticipantePartidaCuadro_HyperLinkJugador$")
                link = player_match_el.find("a", id=link_player_pat_re)["href"]
                if player_info["level"]:
                    player_info["level"] = parse_player_level(player_info["level"])
                else:
                    # Fetch in direct link
                    # https://urbanpadellausanne.matchpoint.com.es/Perfil.aspx?id=159e8bb24a5a9400ea274018c752379d&return_url=https%3a%2f%2furbanpadellausanne.matchpoint.com.es%2fMatches%2fGrid.aspx%3ff%3d21%2f05%2f2025%26c%3d3
                    # url = urban_link_prefix + link
                    # print(url)
                    # fetch_player_level(url)
                    pass
                p = ScrapePlayer(
                    name=player_info["name"].strip(), 
                    level=player_info["level"], 
                    link=link, 
                    position=player_info["position"]
                    )
                p.upd_from_url()
                players.append(p)
            except ValueError as e:
                if "libre" in str(e).lower():
                    players.append(EmptyPlayer)
                else:
                    assert 0
            # except Exception as e:
                # print(e)
                # print(player)
                # traceback.print_exc()
                # assert 0

        return UrbanMatch(
            date=datetime.strptime(f"{date.today()} {start_time}", "%Y-%m-%d %H:%M"),
            location="Lausanne",
            level=(min_level + max_level) / 2,
            a_team=tuple(players[:2]),
            b_team=tuple(players[-2:]),
            court=court
        )
    else:
        return None

def parse_match_players(match_url: str):
    m_response = requests.get(urban_link_prefix + match_url)
    m_soup = BeautifulSoup(m_response.text, "html.parser")



def get_matches() -> list[Match]:
    """Main function to return a list of Match objects."""
    html = get_page_html()
    soup = BeautifulSoup(html, "html.parser")
    match_elements = soup.find_all("div", class_="contenedorContenidoPartidas")

    matches = []
    for el in match_elements:
        try:
            match = parse_match_element(el)
            matches.append(match)
        except Exception as e:
            print(f"[Warning] Failed to parse a match block: {e}")
            continue

    return matches

def get_matches2() -> list[Match]:
    """Main function to return a list of Match objects with a different URL."""

    today = date.today()

    matches = []

    for i in range(DAY_CHECKING_PERIOD):
        day = today + timedelta(days=i)
        print(day.isoformat())  # YYYY-MM-DD string

        print(type(day))

        html = get_page_html2(day)
        soup = BeautifulSoup(html, "html.parser")
        # print(soup)
        # match_elements = soup.find_all("div", class_="contenedorContenidoPartidas")
        # match_elements = soup.find_all("div", class_="contenedoresBannersPartidas")

        # Find all divs with class "gridviewestilocabecera"
        header_divs = soup.find_all("div", class_="gridviewestilocabecera")

        for header_div in header_divs:
            # print(header_div)
            # try:
            match = parse_match_element2(header_div)
            if match:
                match.date = match.date.replace(year=day.year, month=day.month, day=day.day)
                matches.append(match)
            # except Exception as e:
            #     print(f"[Warning] Failed to parse a match block: {e}")
            #     assert 0
            #     continue

            # Get the **next sibling div** that contains players info
            # players_div = header_div.find_next_sibling("div")
            # if players_div:
            #     players_text = players_div.get_text(separator=" ", strip=True)
            # else:
            #     players_text = "No player info found"

    return matches

if __name__ == "__main__":
    matches = get_matches2()
    for m in matches:
        if m.players_needed > 0:
            if m.min_level <= MY_LEVEL <= m.max_level:
                print(m)
                if m:
                    print(m.a_team)
                    print(m.b_team)