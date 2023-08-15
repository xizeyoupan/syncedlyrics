"""NetEase (music.163.com) china-based provider"""

from typing import Optional, Tuple
import json
from rapidfuzz.fuzz import partial_ratio
from .base import LRCProvider
from ..utils import format_lyrics

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9,fa;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "NMTID=00OAVK3xqDG726ITU6jopU6jF2yMk0AAAGCO8l1BA; JSESSIONID-WYYY=8KQo11YK2GZP45RMlz8Kn80vHZ9%2FGvwzRKQXXy0iQoFKycWdBlQjbfT0MJrFa6hwRfmpfBYKeHliUPH287JC3hNW99WQjrh9b9RmKT%2Fg1Exc2VwHZcsqi7ITxQgfEiee50po28x5xTTZXKoP%2FRMctN2jpDeg57kdZrXz%2FD%2FWghb%5C4DuZ%3A1659124633932; _iuqxldmzr_=32; _ntes_nnid=0db6667097883aa9596ecfe7f188c3ec,1659122833973; _ntes_nuid=0db6667097883aa9596ecfe7f188c3ec; WNMCID=xygast.1659122837568.01.0; WEVNSM=1.0.0; WM_NI=CwbjWAFbcIzPX3dsLP%2F52VB%2Bxr572gmqAYwvN9KU5X5f1nRzBYl0SNf%2BV9FTmmYZy%2FoJLADaZS0Q8TrKfNSBNOt0HLB8rRJh9DsvMOT7%2BCGCQLbvlWAcJBJeXb1P8yZ3RHA%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee90c65b85ae87b9aa5483ef8ab3d14a939e9a83c459959caeadce47e991fbaee82af0fea7c3b92a81a9ae8bd64b86beadaaf95c9cedac94cf5cedebfeb7c121bcaefbd8b16dafaf8fbaf67e8ee785b6b854f7baff8fd1728287a4d1d246a6f59adac560afb397bbfc25ad9684a2c76b9a8d00b2bb60b295aaafd24a8e91bcd1cb4882e8beb3c964fb9cbd97d04598e9e5a4c6499394ae97ef5d83bd86a3c96f9cbeffb1bb739aed9ea9c437e2a3; WM_TID=AAkRFnl03RdABEBEQFOBWHCPOeMra4IL; playerid=94262567",
}


class NetEase(LRCProvider):
    """NetEase provider class"""

    API_ENDPOINT_METADATA = "https://music.163.com/api/search/pc"
    API_ENDPOINT_LYRICS = "https://music.163.com/api/song/lyric"

    def __init__(self) -> None:
        super().__init__()
        self.session.headers.update(headers)

    async def search_track(self, search_term: str, duration: int = -1, max_deviation: int = 2000) -> Tuple[Optional[dict], int, int]:
        """Returns a `dict` containing some metadata for the found track."""
        params = {"limit": 20, "type": 1, "offset": 0, "s": search_term}
        response = await self.session.get(self.API_ENDPOINT_METADATA, params=params)
        text = await response.text()
        _json = json.loads(text)
        results = _json.get("result", {}).get("songs")
        if not results:
            return

        target = []
        if duration >= 0:
            for song in results:
                offset = abs(duration - song["duration"])
                if offset <= max_deviation:
                    target.append([song, partial_ratio(search_term, song["name"]), offset])
        else:
            target = [(song, partial_ratio(search_term, song["name"]), 0) for song in results]

        if not target:
            return None

        target = sorted(target, key=lambda x: (x[1], -x[2], ), reverse=True)[0]

        return target

    async def get_lrc_by_id(self, track_id: str) -> Optional[str]:
        params = {"id": track_id, "lv": -1, "tv": -1}
        response = await self.session.get(self.API_ENDPOINT_LYRICS, params=params)
        text = await response.text()
        _json = json.loads(text)
        lrc = _json.get("lrc", {}).get("lyric") or ''
        tlyric = _json.get("tlyric", {}).get("lyric") or ''
        lrc = format_lyrics(lrc, tlyric)
        if not lrc:
            return
        return lrc

    async def get_lrc(self, search_term: str, duration: int = -1, max_deviation: int = 2000) -> Tuple[Optional[str], int, int]:
        track = await self.search_track(search_term, duration, max_deviation)
        if not track:
            return
        return (await self.get_lrc_by_id(track[0]["id"]), track[1], track[2])
