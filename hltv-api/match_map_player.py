from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional

from utils import get_id_from_player_url


# Some map stat pages do not have flash assists
# https://www.hltv.org/stats/matches/mapstatsid/151341/ination-vs-apeks
class MatchMapPlayer:
    """
    Player statistics for a single map of a match.
    """

    def __init__(self, player_tr: WebElement, hltv_match_map_id: int, hltv_team_id: int, side: str):
        """
        Initialize a new MatchMapPlayer object.

        Parameters
        ----------
        stats_tr : WebElement
            Table row element that contains player stats.

        hltv_match_map_id : int
            HLTV's match map ID.

        hltv_team_id : int
            The HLTV team ID of the team the player played with.

        side : str
            Side that the player stats are associated with (e.g., "Both", "T', or "CT").
        """
        self.hltv_player_id: int = self._get_hltv_player_id(player_tr)
        self.hltv_match_map_id: int = hltv_match_map_id
        self.hltv_team_id: int = hltv_team_id
        self.side: str = side
        self.kills: int = self._get_kills(player_tr)
        self.assists: int = self._get_assists(player_tr)
        self.flash_assists: int | None = self._get_flash_assists(player_tr)
        self.deaths: int = int(player_tr.find_element(By.CLASS_NAME, "st-deaths").text)
        self.headshots: int = self._get_headshots(player_tr)
        self.first_kills: int = self._get_first_kills(player_tr)
        self.first_deaths: int = self._get_first_deaths(player_tr)
        self.kast_percent: float = float(
            player_tr.find_element(By.CLASS_NAME, "st-kdratio").text.replace("%", "")
        )
        self.adr: float = float(player_tr.find_element(By.CLASS_NAME, "st-adr").text)
        self.hltv_rating: float = float(player_tr.find_element(By.CLASS_NAME, "st-rating").text)

    def __str__(self) -> str:
        s: str = "MatchMapPlayer:\n"
        attrs = vars(self)
        for key, value in attrs.items():
            s += f"{str(key)}: {str(value)}\n"
        s += "\n"
        return s

    def _get_hltv_player_id(self, player_tr: WebElement) -> int:
        player_cell = player_tr.find_element(By.CLASS_NAME, "st-player")
        player_link = player_cell.find_element(By.TAG_NAME, "a")
        player_url = player_link.get_attribute("href")
        hltv_player_id = get_id_from_player_url(player_url)
        return hltv_player_id

    def _get_kills(self, player_tr: WebElement) -> int:
        kills_cell = player_tr.find_element(By.CLASS_NAME, "st-kills")
        kills = int(kills_cell.text.split()[0].replace('"', "").strip())
        return kills

    def _get_assists(self, player_tr: WebElement) -> int:
        assists_cell = player_tr.find_element(By.CLASS_NAME, "st-assists")
        assists = int(assists_cell.text.split()[0].replace('"', "").strip())
        return assists

    def _get_flash_assists(self, player_tr: WebElement) -> int | None:
        assists_cell = player_tr.find_element(By.CLASS_NAME, "st-assists")
        assist_spans = assists_cell.find_elements(By.TAG_NAME, "span")
        flash_assists = None
        if len(assist_spans) > 0:
            # Some map stat pages do not show flash assist count next to assist count
            flash_assists = int(assist_spans[0].text.replace("(", "").replace(")", "").strip())
        return flash_assists

    def _get_headshots(self, player_tr: WebElement) -> int:
        kills_cell = player_tr.find_element(By.CLASS_NAME, "st-kills")
        headshots_span = kills_cell.find_element(By.TAG_NAME, "span")
        headshots = int(headshots_span.text.replace("(", "").replace(")", "").strip())
        return headshots

    def _get_first_kills(self, player_tr: WebElement) -> int:
        fk_diff_cell = player_tr.find_element(By.CLASS_NAME, "st-fkdiff")
        fk_diff_desc = fk_diff_cell.get_attribute(
            "title"
        )  # e.g., "3 first kills, 2 first deaths in a round"
        fk_diff_desc_split = fk_diff_desc.split()
        first_kills = int(fk_diff_desc_split[0])
        return first_kills

    def _get_first_deaths(self, player_tr: WebElement):
        fk_diff_cell = player_tr.find_element(By.CLASS_NAME, "st-fkdiff")
        fk_diff_desc = fk_diff_cell.get_attribute(
            "title"
        )  # e.g., "3 first kills, 2 first deaths in a round"
        fk_diff_desc_split = fk_diff_desc.split()
        first_deaths = int(fk_diff_desc_split[3])
        return first_deaths
