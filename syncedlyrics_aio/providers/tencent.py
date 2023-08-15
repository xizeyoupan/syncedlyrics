"""Tencent (y.qq.com) china-based provider"""

import base64
import html
from typing import Optional, Tuple
import json
import urllib
from rapidfuzz.fuzz import partial_ratio
from .base import LRCProvider
from ..utils import format_lyrics

headers = {
    "Referer": "'https://y.qq.com'",
}


class Tencent(LRCProvider):
    """Tencent provider class"""

    API_ENDPOINT_METADATA = "https://shc6.y.qq.com/soso/fcgi-bin/search_for_qq_cp"
    API_ENDPOINT_LYRICS = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"

    def __init__(self) -> None:
        super().__init__()
        self.session.headers.update(headers)

    async def search_track(self, search_term: str, duration: int = -1, max_deviation: int = 2000) -> Tuple[Optional[dict], int, int]:
        params = {
            "format": 'json',
            "n": 20,
            "p": 1,
            "w": search_term,
            "cr": 1,
            "g_tk": 5381,
            "t": 0
        }
        response = await self.session.get(self.API_ENDPOINT_METADATA, params=params)
        text = await response.text()
        _json = json.loads(text)
        results = _json.get("data", {}).get("song")['list']
        if not results:
            return

        target = []
        if duration >= 0:
            for song in results:
                offset = abs(duration - song["interval"] * 1000)
                if offset <= max_deviation:
                    target.append((song, partial_ratio(search_term, song["songname"]), offset))
        else:
            target = [(song, partial_ratio(search_term, song["songname"]), 0) for song in results]

        if not target:
            return None

        target = sorted(target, key=lambda x: (x[1], -x[2], ), reverse=True)[0]

        return target

    async def get_lrc_by_id(self, track_id: str) -> Optional[str]:
        params = {
            "songmid": track_id,

            "g_tk": 5381,
            "loginUin": 0,
            "hostUin": 0,
            "inCharset": 'utf8',
            "outCharset": 'utf-8',
            "notice": 0,
            "platform": 'yqq',
            "needNewCode": 0,
            "format": "json"
        }
        response = await self.session.get(self.API_ENDPOINT_LYRICS, params=params)
        text = await response.text()
        _json = json.loads(text)

        lrc = _json.get("lyric", '')
        decoded_uri = urllib.parse.unquote(lrc)
        lrc = base64.b64decode(decoded_uri).decode("utf-8")
        lrc = html.unescape(lrc)

        tlyric = _json.get("trans", '')
        decoded_uri = urllib.parse.unquote(tlyric)
        tlyric = base64.b64decode(decoded_uri).decode("utf-8")
        tlyric = html.unescape(tlyric)

        lrc = format_lyrics(lrc, tlyric)
        if not lrc:
            return
        return lrc

    async def get_lrc(self, search_term: str, duration: int = -1, max_deviation: int = 2000) -> Tuple[Optional[str], int, int]:
        track = await self.search_track(search_term, duration, max_deviation)
        if not track:
            return
        return (await self.get_lrc_by_id(track[0]["songmid"]), track[1], track[2])
