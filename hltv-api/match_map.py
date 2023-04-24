from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from typing import List, Optional

# from match_map_player import MatchMapPlayer
from utils import get_id_from_match_map_url, get_id_from_match_url, get_id_from_team_url


class MatchMap:
    """
    Information about a single map in a match, such as the map name,
    team round wins, and team-based stats.
    """

    def __init__(self, driver: WebDriver, url: str, match_id: int):
        """
        Initialize a new MatchMap object.

        Parameters
        ----------
        driver : WebDriver
            The Selenium WebDriver instance to use to fetch the match data.

        url : str
            The URL of HLTV's match map stats page.

        match_id : int
            The HLTV ID of the match.
        """
        driver.get(url)
        sleep(5)

        self.hltv_match_map_id: int = get_id_from_match_map_url(url)
        self.hltv_match_id: Optional[int] = match_id

        self.map_number: Optional[int] = None
        self.map_name: Optional[str] = None
        # self.map_picked_by: Optional[int] = None
        self._set_map_attributes(driver)

        self.team1_hltv_team_id: Optional[int] = None
        self.team1_rounds_won: Optional[int] = None
        self._set_team_ids_and_rounds_won(driver=driver, team_num=1)

        self.team2_hltv_team_id: Optional[int] = None
        self.team2_rounds_won: Optional[int] = None
        self._set_team_ids_and_rounds_won(driver=driver, team_num=2)

        self.team1_1h_side: Optional[str] = None  # "T" or "CT"
        self.team1_1h_rounds_won: Optional[int] = None
        self.team1_2h_side: Optional[str] = None
        self.team1_2h_rounds_won: Optional[int] = None
        self.team2_1h_side: Optional[str] = None
        self.team2_1h_rounds_won: Optional[int] = None
        self.team2_2h_side: Optional[str] = None
        self.team2_2h_rounds_won: Optional[int] = None
        self._set_team_1h_2h_data(driver)

        # self.team1_kills: Optional[int] = None
        # self.team1_assists: Optional[int] = None
        # self.team1_first_kills: Optional[int] = None
        # self.team2_kills: Optional[int] = None
        # self.team2_deaths: Optional[int] = None
        # self.team2_assists: Optional[int] = None
        # self.team2_first_kills: Optional[int] = None

        self.team1_bombs_exploded: Optional[int] = None
        self.team1_bombs_defused: Optional[int] = None
        self.team2_bombs_exploded: Optional[int] = None
        self.team2_bombs_defused: Optional[int] = None
        self._set_team_bomb_stats(driver)

    def __str__(self) -> str:
        s: str = "MatchMap:\n"
        attrs = vars(self)
        for key, value in attrs.items():
            s += f"{str(key)}: {str(value)}\n"
        s += "\n"
        return s

    def _get_hltv_match_id(self, driver: WebDriver) -> int:
        match_link = driver.find_element(By.CLASS_NAME, "match-page-link")
        match_url = match_link.get_attribute("href")
        hltv_match_id = get_id_from_match_url(match_url)
        return hltv_match_id

    def _set_map_attributes(self, driver: WebDriver):
        match_info_box = driver.find_element(By.CLASS_NAME, "match-info-box")
        map_name = match_info_box.text.split("Map")[1].split("\n")[1].strip()
        map_divs = driver.find_elements(By.CLASS_NAME, "stats-match-map")
        if len(map_divs) == 0:  # Best of 1
            self.map_number = 1
            self.map_name = map_name
            return
        map_divs = map_divs[1:]  # First div contains the series score. Ignore
        map_num = 0
        active_map_div: Optional[WebElement] = None
        for i in range(0, len(map_divs)):
            if "inactive" not in map_divs[i].get_attribute("class"):
                map_num = i + 1
                active_map_div = map_divs[i]
                break
        if active_map_div != None:
            self.map_number = map_num
            self.map_name = active_map_div.find_element(By.CLASS_NAME, "dynamic-map-name-full").text

    def _set_team_ids_and_rounds_won(self, driver: WebDriver, team_num):
        div_side = "left" if team_num == 1 else "right"
        team_div = driver.find_element(By.CLASS_NAME, f"team-{div_side}")
        team_link = team_div.find_element(By.TAG_NAME, "a")
        team_url = team_link.get_attribute("href")
        rounds_won = int(team_div.find_element(By.TAG_NAME, "div").text)
        setattr(self, f"team{team_num}_hltv_team_id", get_id_from_team_url(team_url))
        setattr(self, f"team{team_num}_rounds_won", rounds_won)

    def _set_team_1h_2h_data(self, driver: WebDriver):
        # Rounds won by side
        match_info_box_div = driver.find_element(By.CLASS_NAME, "match-info-box-con")
        match_info_row_divs = match_info_box_div.find_elements(By.CLASS_NAME, "match-info-row")
        round_breakdown_div = match_info_row_divs[0]
        round_spans = round_breakdown_div.find_elements(By.TAG_NAME, "span")
        # span 1: Team 1 rounds won
        # span 2: Team 2 rounds won
        # span 3: Team 1 first half rounds won (class name will indicate side- "t-color" or "ct-color")
        # span 4: Team 2 first half rounds won
        # span 5: Team 1 second half rounds won
        # span 6: Team 2 second half rounds won
        self.team1_1h_side = round_spans[2].get_attribute("class").replace("-color", "").upper()
        self.team1_1h_rounds_won = int(round_spans[2].text)
        self.team1_2h_side = round_spans[4].get_attribute("class").replace("-color", "").upper()
        self.team1_2h_rounds_won = int(round_spans[4].text)

        self.team2_1h_side = round_spans[3].get_attribute("class").replace("-color", "").upper()
        self.team2_1h_rounds_won = int(round_spans[3].text)
        self.team2_2h_side = round_spans[5].get_attribute("class").replace("-color", "").upper()
        self.team2_2h_rounds_won = int(round_spans[5].text)

    def _set_team_bomb_stats(self, driver: WebDriver):
        # Bombs exploded & defused
        round_history_team_divs = driver.find_elements(By.CLASS_NAME, "round-history-team-row")
        self.team1_bombs_exploded = self.get_bombs_exploded(round_history_team_divs[0])
        self.team1_bombs_defused = self.get_bombs_defused(round_history_team_divs[0])
        self.team2_bombs_exploded = self.get_bombs_exploded(round_history_team_divs[1])
        self.team2_bombs_defused = self.get_bombs_defused(round_history_team_divs[1])

    def get_bombs_defused(self, round_history_div: WebElement) -> int:
        round_images = round_history_div.find_elements(By.TAG_NAME, "img")
        bombs_defused = 0
        for round_image in round_images:
            if "bomb_defused" in round_image.get_attribute("src"):
                bombs_defused += 1
        return bombs_defused

    def get_bombs_exploded(self, round_history_div: WebElement) -> int:
        round_images = round_history_div.find_elements(By.TAG_NAME, "img")
        bombs_exploded = 0
        for round_image in round_images:
            if "bomb_exploded" in round_image.get_attribute("src"):
                bombs_exploded += 1
        return bombs_exploded
