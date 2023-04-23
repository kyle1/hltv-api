from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from time import sleep
from typing import List
import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions

from match import Match
from result import Result


class HltvClient:
    def __init__(self):
        self._driver = self._initialize_undetected_chromedriver()

    def _initialize_undetected_chromedriver(self) -> WebDriver:
        options: ChromeOptions = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--headless") # Currently does not work with undetected_chromedriver
        driver: WebDriver = uc.Chrome(use_subprocess=True, options=options, version_main=111)
        return driver

    def quit(self):
        self._driver.quit()

    def get_results(self, offset_start: int = 0, offset_end: int = 0) -> List[Result]:
        results: List[Result] = []
        current_offset = offset_start
        while current_offset <= offset_end:
            self._driver.get(f"https://www.hltv.org/results?offset={current_offset}")
            sleep(5)  # Give time for page to load
            for result_div in self._driver.find_elements(By.CLASS_NAME, "result-con"):
                if result_div.get_attribute("data-zonedgrouping-entry-unix") == None:
                    # If the result div does not have the unix attribute, it is one
                    # of the featured results at the top of the page. Skip these.
                    continue
                result = Result(result_div)
                results.append(result)
            current_offset += 100
        return results

    def get_match(self, match_url) -> Match:
        match = Match(match_url=match_url, driver=self._driver)
        return match
