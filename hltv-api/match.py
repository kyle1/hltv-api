from datetime import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from typing import List, Optional, Union

from pick_ban import PickBan
from utils import get_id_from_event_url, get_id_from_match_url, get_id_from_team_url


class Match:
    """
    Detailed information about the final statistics for a match.

    Parameters
    ----------
    match_url : str
        The URL for the match page.

    driver : WebDriver
        An instance of Selenium's Chrome WebDriver that will be used to fetch the match data.
    """

    def __init__(self, match_url: str, driver: WebDriver):
        driver.get(match_url)
        sleep(5)

        skip_keywords = ["forfeit", "default", "withdrew", "withdraw", "showmatch"]
        # The veto box will state if the match had a forfeiture, was a showmatch, etc.
        veto_text = driver.find_element(By.CLASS_NAME, "veto-box").text
        if any(map(veto_text.__contains__, skip_keywords)):
            self.skipped = True
            return

        self.hltv_match_id: int = get_id_from_match_url(match_url)
        self.match_date: datetime = self._get_match_date(driver)
        self.match_url: str = match_url
        self.hltv_event_id: int = self._get_hltv_event_id(driver)
        self.best_of: Optional[int] = self._get_best_of(driver)
        self.team1_name: Optional[str] = None
        self.team1_hltv_team_id: Optional[int] = None
        self.team1_maps_won: Optional[int] = None
        self.team1_world_rank: Optional[int] = None
        self.team2_name: Optional[str] = None
        self.team2_hltv_team_id: Optional[int] = None
        self.team2_maps_won: Optional[int] = None
        self.team2_world_rank: Optional[int] = None

        self._set_team_values(team_num=1, driver=driver)
        self._set_team_values(team_num=2, driver=driver)

        self.pick_bans: List[PickBan] = self._get_pick_bans(driver)

    def __str__(self) -> str:
        s: str = "Match:\n"
        attrs = vars(self)
        for key, value in attrs.items():
            s += f"{str(key)}: {str(value)}\n"
        s += "\n"
        return s

    def _set_team_values(self, driver: WebDriver, team_num: int):
        teams_div = driver.find_element(By.XPATH, "//div[@class='standard-box teamsBox']")
        team_div = teams_div.find_elements(By.CLASS_NAME, "team")[team_num - 1]
        setattr(self, f"team{team_num}_name", team_div.find_element(By.CLASS_NAME, "teamName").text)
        setattr(self, f"team{team_num}_hltv_team_id", self._get_hltv_team_id(team_div))
        setattr(self, f"team{team_num}_maps_won", self._get_team_maps_won(team_div))
        rank_text = driver.find_elements(By.CLASS_NAME, "teamRanking")[team_num - 1].text
        if rank_text != "Unranked":
            # Parse rank value from text (e.g. "World rank: #35")
            setattr(self, f"team{team_num}_world_rank", int(rank_text.split("#")[1]))

    def _get_match_date(self, driver: WebDriver) -> datetime:
        date_div = driver.find_element(By.CLASS_NAME, "date")
        timestamp = float(date_div.get_attribute("data-unix")) / 1000
        return datetime.fromtimestamp(timestamp)

    def _get_best_of(self, driver: WebDriver) -> int | None:
        best_of_div = driver.find_element(By.CLASS_NAME, "preformatted-text")
        if "Best of " in best_of_div.text:
            return int(best_of_div.text.split("Best of ")[1][0])
        return None

    def _get_hltv_event_id(self, driver: WebDriver) -> int:
        event_div = driver.find_element(By.CLASS_NAME, "event")
        event_link = event_div.find_element(By.TAG_NAME, "a")
        event_url = event_link.get_attribute("href")
        return get_id_from_event_url(event_url)

    def _get_hltv_team_id(self, team_div: WebElement) -> int:
        team_url = team_div.find_element(By.TAG_NAME, "a").get_attribute("href")
        hltv_team_id = get_id_from_team_url(team_url)
        return hltv_team_id

    def _get_team_maps_won(self, team_div: WebElement) -> Union[int, None]:
        won_divs = team_div.find_elements(By.CLASS_NAME, "won")
        lost_divs = team_div.find_elements(By.CLASS_NAME, "lost")
        map_wins = None
        if len(won_divs) > 0:
            map_wins = int(won_divs[0].text)
        elif len(lost_divs) > 0:
            map_wins = int(lost_divs[0].text)
        return map_wins

    def _get_pick_bans(self, driver: WebDriver) -> List[PickBan]:
        # Pick/bans are nested in the second "veto-box" div
        veto_box_div = driver.find_elements(By.CLASS_NAME, "veto-box")[1]
        veto_box_inner_div = veto_box_div.find_element(By.CLASS_NAME, "padding")
        pick_number = 0
        pick_bans: List[PickBan] = []
        # Last pick/ban div is the decider map, which can be ignored
        for pb_div in veto_box_inner_div.find_elements(By.TAG_NAME, "div")[:-1]:
            pick_number += 1
            hltv_team_id = None
            team_name = " ".join(pb_div.text.split()[1:-2])
            if team_name == self.team1_name:
                hltv_team_id = self.team1_hltv_team_id
            elif team_name == self.team2_name:
                hltv_team_id = self.team2_hltv_team_id
            if hltv_team_id == None:
                continue
            pick_type = "Pick" if "picked" in pb_div.text else "Ban"
            map_name = pb_div.text.split()[-1]
            pb = PickBan(
                hltv_match_id=self.hltv_match_id,
                pick_number=pick_number,
                hltv_team_id=hltv_team_id,
                pick_type=pick_type,
                map_name=map_name,
            )
            pick_bans.append(pb)
        return pick_bans
