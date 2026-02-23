"""
Oscar Winning Films Crawler - Strategy: Selenium with dynamic JavaScript rendering.
Target: https://www.scrapethissite.com/pages/ajax-javascript/

The Oscar page loads film data dynamically by clicking year buttons and waiting
for AJAX responses to populate the table. We use Selenium to automate this.
"""
import logging
import time
from typing import List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.config import settings

logger = logging.getLogger(__name__)


def _build_driver() -> webdriver.Chrome:
    """Creates a headless Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def _parse_films_from_table(driver: webdriver.Chrome) -> List[Dict[str, Any]]:
    """Parse film rows from the currently rendered AJAX table."""
    films = []
    rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr.film")
    for row in rows:
        try:
            title = row.find_element(By.CSS_SELECTOR, "td.film-title").text.strip()
            nominations = int(row.find_element(By.CSS_SELECTOR, "td.film-nominations").text.strip())
            awards = int(row.find_element(By.CSS_SELECTOR, "td.film-awards").text.strip())
            best_picture_el = row.find_elements(By.CSS_SELECTOR, "td.film-best-picture i.glyphicon-ok")
            best_picture = len(best_picture_el) > 0

            films.append({
                "title": title,
                "nominations": nominations,
                "awards": awards,
                "best_picture": best_picture,
            })
        except Exception as e:
            logger.warning(f"Could not parse film row: {e}")
    return films


def scrape_oscar_films() -> List[Dict[str, Any]]:
    """
    Crawls the Oscar page year by year, clicking each year button,
    waiting for the AJAX table to load, and scraping the results.
    Returns all films across all years.
    """
    all_films: List[Dict[str, Any]] = []
    driver = _build_driver()

    try:
        logger.info(f"Opening Oscar URL: {settings.OSCAR_URL}")
        driver.get(settings.OSCAR_URL)

        # Wait for year buttons to appear
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.year-link")))

        # Collect all year buttons text and hrefs
        year_buttons = driver.find_elements(By.CSS_SELECTOR, "a.year-link")
        years = [btn.text.strip() for btn in year_buttons]
        logger.info(f"Found {len(years)} year buttons: {years}")

        for year in years:
            logger.info(f"Clicking year: {year}")
            # Re-locate buttons each iteration to avoid stale elements
            btn = driver.find_element(By.XPATH, f"//a[@class='year-link' and normalize-space(text())='{year}']")
            btn.click()

            # Wait for the table to load with film rows
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tbody tr.film")))
            time.sleep(0.5)  # Small buffer for full render

            films = _parse_films_from_table(driver)
            for film in films:
                film["year"] = year  # Tag with the year

            logger.info(f"Year {year}: {len(films)} films scraped.")
            all_films.extend(films)

    finally:
        driver.quit()

    logger.info(f"Total Oscar films scraped: {len(all_films)}")
    return all_films
