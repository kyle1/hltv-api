from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from utils import get_id_from_match_url


class Result:
    """
    Results for a match. This object contains basic result information such
    as match date, teams, and final score. Detailed match information and
    stats are contained within the Match class.
    """

    def __init__(self, result_div: WebElement):
        """
        Initialize a new Result object.

        Parameters
        ----------
        driver : WebDriver
            The Selenium WebDriver instance to use to fetch the data.

        result_div : WebElement
            The div element that contains the result information.
        """

        self.match_url = result_div.find_element(By.TAG_NAME, "a").get_attribute("href")
        self.hltv_match_id = get_id_from_match_url(self.match_url)
        self.match_date = datetime.fromtimestamp(
            float(result_div.get_attribute("data-zonedgrouping-entry-unix")) / 1000
        )
        self.team1_name = result_div.find_element(By.CLASS_NAME, "team1").text
        self.team1_score = self._parse_score(result_div=result_div, team_num=1)
        self.team2_name = result_div.find_element(By.CLASS_NAME, "team2").text
        self.team2_score = self._parse_score(result_div=result_div, team_num=2)

    def _parse_score(self, result_div: WebElement, team_num: int) -> int:
        score_cell = result_div.find_element(By.CLASS_NAME, "result-score")
        return int(score_cell.find_elements(By.TAG_NAME, "span")[team_num - 1].text)
