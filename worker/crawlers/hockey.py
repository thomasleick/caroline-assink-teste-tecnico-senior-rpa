"""
Hockey Teams Crawler - Strategy: HTML scraping with httpx + BeautifulSoup.
Target: https://www.scrapethissite.com/pages/forms/
"""
import logging
import re
from typing import List, Dict, Any

import httpx
from bs4 import BeautifulSoup

from core.config import settings

logger = logging.getLogger(__name__)

PAGE_SIZE = 25  # default rows per page on the site


def _parse_int(value: str) -> int | None:
    """Safely parse a string to int, returning None on failure."""
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None


def _parse_float(value: str) -> float | None:
    """Safely parse a string to float, returning None on failure."""
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None


def _parse_page(html: str) -> List[Dict[str, Any]]:
    """Parse a single HTML page and return a list of team dicts."""
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table.table tbody tr")
    teams = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 9:
            continue
        teams.append({
            "team_name": cells[0].get_text(strip=True),
            "year": _parse_int(cells[1].get_text()),
            "wins": _parse_int(cells[2].get_text()),
            "losses": _parse_int(cells[3].get_text()),
            "ot_losses": _parse_int(cells[4].get_text()),
            "win_percentage": _parse_float(cells[5].get_text()),
            "goals_for": _parse_int(cells[6].get_text()),
            "goals_against": _parse_int(cells[7].get_text()),
            "goal_difference": _parse_int(cells[8].get_text()),
        })
    return teams


def _get_total_pages(html: str) -> int:
    """Parse total number of pages from pagination info on the first page."""
    soup = BeautifulSoup(html, "html.parser")
    # The site shows total teams count somewhere, let's find the pagination
    pagination = soup.select("ul.pagination li a")
    max_page = 1
    for link in pagination:
        href = link.get("href", "")
        match = re.search(r"page_num=(\d+)", href)
        if match:
            page_num = int(match.group(1))
            if page_num > max_page:
                max_page = page_num
    return max_page


async def scrape_hockey_teams() -> List[Dict[str, Any]]:
    """
    Crawls all pages of the Hockey Teams table and returns a flat list of records.
    Uses httpx async client for non-blocking HTTP.
    """
    all_teams: List[Dict[str, Any]] = []
    base_url = settings.HOCKEY_URL

    async with httpx.AsyncClient(timeout=30) as client:
        # Fetch first page to determine total pages
        logger.info(f"Fetching first page: {base_url}")
        response = await client.get(base_url)
        response.raise_for_status()
        html = response.text

        all_teams.extend(_parse_page(html))
        total_pages = _get_total_pages(html)
        logger.info(f"Found {total_pages} pages to crawl.")

        # Fetch remaining pages
        for page in range(2, total_pages + 1):
            page_url = f"{base_url}?page_num={page}"
            logger.info(f"Fetching page {page}/{total_pages}: {page_url}")
            response = await client.get(page_url)
            response.raise_for_status()
            all_teams.extend(_parse_page(response.text))

    logger.info(f"Scraped {len(all_teams)} hockey team records in total.")
    return all_teams
