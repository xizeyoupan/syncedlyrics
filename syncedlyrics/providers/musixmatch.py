"""Musixmatch LRC provider"""

import json
from typing import Optional, Tuple
from .base import LRCProvider


class Musixmatch(LRCProvider):
    """Musixmatch provider class"""

    USER_TOKEN = "190523f77464fba06fa5f82a9bfab0aa9dc201244ecf5124a06d95"
    SEARCH_ENDPOINT = "https://apic-desktop.musixmatch.com/ws/1.1/track.search?format=json&q={q}&page_size=5&page=1&s_track_rating=desc&quorum_factor=1.0&app_id=web-desktop-app-v1.0&usertoken={token}"
    LRC_ENDPOINT = "https://apic-desktop.musixmatch.com/ws/1.1/track.subtitle.get?format=json&track_id={track_id}&subtitle_format=lrc&app_id=web-desktop-app-v1.0&usertoken={token}"

    async def get_lrc_by_id(self, track_id: str) -> Optional[str]:
        url = self.LRC_ENDPOINT.format(track_id=track_id, token=self.USER_TOKEN)
        r = await self.session.get(url)
        if not r.ok:
            return
        _json = json.loads(await r.text())
        body = _json["message"]["body"]

        if not body:
            return
        return body["subtitle"]["subtitle_body"]

    async def get_lrc(self, search_term: str, duration: int = -1, max_deviation: int = 2000) -> Tuple[Optional[str], int]:
        url = self.SEARCH_ENDPOINT.format(q="".join(search_term.split()), token=self.USER_TOKEN)
        r = await self.session.get(url)
        if not r.ok:
            return
        _json = json.loads(await r.text())
        body = _json["message"]["body"]

        if not body:
            return
        tracks = body["track_list"]
        if not tracks:
            return

        """
        TODO:
        Not sure should use this:
        https://developer.musixmatch.com/documentation/api-reference/matcher-subtitle-get
        """

        return (await self.get_lrc_by_id(tracks[0]["track"]["track_id"]), 20)
