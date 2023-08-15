"""Lrclib (lrclib.net) LRC provider"""

from typing import Optional, Tuple
from rapidfuzz.fuzz import partial_ratio
from .base import LRCProvider


class Lrclib(LRCProvider):
    """Lrclib LRC provider class"""

    ROOT_URL = "https://lrclib.net"
    API_ENDPOINT = ROOT_URL + "/api"
    SEARCH_ENDPOINT = API_ENDPOINT + "/search"
    LRC_ENDPOINT = API_ENDPOINT + "/get/"

    def __init__(self) -> None:
        super().__init__()

    async def get_lrc_by_id(self, track_id: str) -> Optional[str]:
        url = self.LRC_ENDPOINT + track_id
        r = await self.session.get(url)
        if not r.ok:
            return
        track = await r.json()
        return track.get("syncedLyrics", track.get("plainLyrics"))

    async def get_lrc(self, search_term: str, duration: int = -1, max_deviation: int = 2000) -> Tuple[Optional[str], int]:
        """Duration NotImplemented"""
        url = self.SEARCH_ENDPOINT
        r = await self.session.get(url, params={"q": search_term})
        if not r.ok or not r.content:
            print("bad")
            return
        tracks = await r.json()
        if not tracks:
            return
        tracks = sorted([(track, partial_ratio(search_term, track["name"])) for track in tracks], key=lambda x: x[1], reverse=True)

        _id = str(tracks[0][0]["id"])
        return (await self.get_lrc_by_id(_id), tracks[0][1], 10000)
