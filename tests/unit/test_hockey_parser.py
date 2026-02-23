"""
Unit tests for the Hockey crawler's HTML parsing logic.
We mock HTTP responses to avoid real network calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Sample HTML fixture representing a single page of the hockey table
HOCKEY_HTML_SINGLE_PAGE = """
<html>
<body>
<table class="table">
  <tbody>
    <tr>
      <td>Boston Bruins</td>
      <td>1990</td>
      <td>44</td>
      <td>24</td>
      <td>12</td>
      <td>0.563</td>
      <td>299</td>
      <td>264</td>
      <td>35</td>
    </tr>
    <tr>
      <td>Calgary Flames</td>
      <td>1990</td>
      <td>46</td>
      <td>26</td>
      <td>8</td>
      <td>0.600</td>
      <td>344</td>
      <td>263</td>
      <td>81</td>
    </tr>
  </tbody>
</table>
<ul class="pagination">
  <li><a href="?page_num=1">1</a></li>
</ul>
</body>
</html>
"""


def test_parse_page_returns_correct_number_of_teams():
    from worker.crawlers.hockey import _parse_page

    teams = _parse_page(HOCKEY_HTML_SINGLE_PAGE)
    assert len(teams) == 2


def test_parse_page_extracts_correct_values():
    from worker.crawlers.hockey import _parse_page

    teams = _parse_page(HOCKEY_HTML_SINGLE_PAGE)
    assert teams[0]["team_name"] == "Boston Bruins"
    assert teams[0]["year"] == 1990
    assert teams[0]["wins"] == 44
    assert teams[0]["losses"] == 24
    assert teams[0]["ot_losses"] == 12
    assert abs(teams[0]["win_percentage"] - 0.563) < 1e-6
    assert teams[0]["goals_for"] == 299
    assert teams[0]["goals_against"] == 264
    assert teams[0]["goal_difference"] == 35


def test_parse_page_handles_empty_tbody():
    from worker.crawlers.hockey import _parse_page

    html = "<html><body><table class='table'><tbody></tbody></table></body></html>"
    teams = _parse_page(html)
    assert teams == []


def test_get_total_pages_single():
    from worker.crawlers.hockey import _get_total_pages

    total = _get_total_pages(HOCKEY_HTML_SINGLE_PAGE)
    assert total == 1


def test_get_total_pages_multiple():
    from worker.crawlers.hockey import _get_total_pages

    html = """
    <html><body>
    <ul class="pagination">
      <li><a href="?page_num=1">1</a></li>
      <li><a href="?page_num=2">2</a></li>
      <li><a href="?page_num=3">3</a></li>
    </ul>
    </body></html>
    """
    assert _get_total_pages(html) == 3


def test_parse_int_valid():
    from worker.crawlers.hockey import _parse_int

    assert _parse_int("  42  ") == 42


def test_parse_int_invalid():
    from worker.crawlers.hockey import _parse_int

    assert _parse_int("N/A") is None
    assert _parse_int("") is None


def test_parse_float_valid():
    from worker.crawlers.hockey import _parse_float

    assert abs(_parse_float("  0.500  ") - 0.5) < 1e-9


@pytest.mark.asyncio
async def test_scrape_hockey_teams_fetches_all_pages():
    """Integration-style unit test: mock httpx to return controlled HTML."""
    from worker.crawlers.hockey import scrape_hockey_teams

    mock_response = MagicMock()
    mock_response.text = HOCKEY_HTML_SINGLE_PAGE
    mock_response.raise_for_status = MagicMock()

    with patch("worker.crawlers.hockey.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        teams = await scrape_hockey_teams()

    assert len(teams) == 2
    assert teams[1]["team_name"] == "Calgary Flames"
