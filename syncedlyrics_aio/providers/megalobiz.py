"""Megalobiz (megalobiz.com) LRC provider"""

from typing import Optional, Tuple
import re
import rapidfuzz
from bs4 import SoupStrainer
from .base import LRCProvider
from ..utils import generate_bs4_soup


class Megalobiz(LRCProvider):
    """Megabolz provider class"""

    ROOT_URL = "https://www.megalobiz.com"
    SEARCH_ENDPOINT = ROOT_URL + "/search/all?qry={q}&searchButton.x=0&searchButton.y=0"

    async def get_lrc(self, search_term: str, duration: int = -1, max_deviation: int = 2000) -> Tuple[Optional[str], int]:
        url = self.SEARCH_ENDPOINT.format(q=search_term)

        def href_match(h: Optional[str]):
            if h and h.startswith("/lrc/maker/"):
                return True
            return False

        def duration_match(s: str):
            _result = re.findall(r"\d{1,2}:\d{1,2}\.\d{1,2}", s)
            if _result:
                _time = _result[0].split(':')
                _time = list(map(float, _time))
                _duration = _time[0] * 60 * 1000 + _time[1] * 1000
                return _duration
            else:
                return

        a_tags_boud = SoupStrainer("a", href=href_match)
        soup = await generate_bs4_soup(self.session, url, parse_only=a_tags_boud)
        a_tag = soup.find_all("a")
        if not a_tag:
            return None

        reslut = []
        if duration >= 0:
            for tag in a_tag:
                ms = duration_match(tag["title"])
                if not ms:
                    continue
                if duration - max_deviation <= ms <= duration + max_deviation:
                    reslut.append([tag, rapidfuzz.fuzz.token_sort_ratio(search_term, tag["title"])])
        else:
            reslut = [[tag, rapidfuzz.fuzz.token_sort_ratio(search_term, tag["title"])] for tag in a_tag]

        if not reslut:
            return None
        reslut = sorted(reslut, key=lambda x: x[1], reverse=True)[0]

        # Scraping from the LRC page
        lrc_id = reslut[0]["href"].split(".")[-1]
        soup = await generate_bs4_soup(self.session, self.ROOT_URL + reslut[0]["href"])
        return (soup.find("div", {"id": f"lrc_{lrc_id}_details"}).get_text(), reslut[1])
