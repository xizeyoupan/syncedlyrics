"""Tencent (y.qq.com) china-based provider"""

import base64
import html
from typing import Optional, Tuple
import json
import urllib
from rapidfuzz.fuzz import token_sort_ratio
from .base import LRCProvider
from ..utils import Lyrics, get_best_match, format_lyrics


class Tencent(LRCProvider):
    """Tencent provider class"""

    API_ENDPOINT_METADATA = "https://shc6.y.qq.com/soso/fcgi-bin/search_for_qq_cp"
    API_ENDPOINT_LYRICS = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"

    def __init__(self, duration=0, max_deviation=2000) -> None:
        super().__init__()
        self.duration = duration
        self.max_deviation = max_deviation
        headers = {
            "Referer": "'https://y.qq.com'",
        }
        self.session.headers.update(headers)

    async def search_track(self, search_term: str):
        params = {
            "format": "json",
            "n": 20,
            "p": 1,
            "w": search_term,
            "cr": 1,
            "g_tk": 5381,
            "t": 0,
        }
        response = await self.session.get(self.API_ENDPOINT_METADATA, params=params)
        text = await response.text()
        _json = json.loads(text)
        results = _json.get("data", {}).get("song")["list"]

        if self.duration:
            results = list(
                filter(
                    lambda x: abs(self.duration - x["interval"] * 1000)
                    <= self.max_deviation,
                    results,
                )
            )

        if not results:
            return None
        cmp_key = lambda t: f"{t.get('songname')}"
        track = get_best_match(results, search_term, cmp_key)

        return track

    async def get_lrc_by_id(self, track_id: str) -> Optional[Lyrics]:
        params = {
            "songmid": track_id,
            "g_tk": 5381,
            "loginUin": 0,
            "hostUin": 0,
            "inCharset": "utf8",
            "outCharset": "utf-8",
            "notice": 0,
            "platform": "yqq",
            "needNewCode": 0,
            "format": "json",
        }
        response = await self.session.get(self.API_ENDPOINT_LYRICS, params=params)
        text = await response.text()
        _json = json.loads(text)

        lrc = _json.get("lyric", "")
        decoded_uri = urllib.parse.unquote(lrc)
        lrc = base64.b64decode(decoded_uri).decode("utf-8")
        lrc = html.unescape(lrc)

        tlyric = _json.get("trans", "")
        decoded_uri = urllib.parse.unquote(tlyric)
        tlyric = base64.b64decode(decoded_uri).decode("utf-8")
        tlyric = html.unescape(tlyric)

        lrc_text = format_lyrics(lrc, tlyric)
        if not lrc:
            return
        lrc = Lyrics()
        lrc.add_unknown(lrc_text)
        return lrc

    async def get_lrc(self, search_term: str):
        track = await self.search_track(search_term)
        if not track:
            return
        return await self.get_lrc_by_id(track["songmid"])
