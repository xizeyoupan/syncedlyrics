"""Musixmatch LRC provider"""

import json
from typing import List, Optional, Tuple
from .base import LRCProvider
import time
import os
from rapidfuzz.fuzz import partial_ratio

# Inspired from https://github.com/Marekkon5/onetagger/blob/0654131188c4df2b4b171ded7cdb927a4369746e/crates/onetagger-platforms/src/musixmatch.rs
# Huge part converted from Rust to Py by ChatGPT :)


class Musixmatch(LRCProvider):
    """Musixmatch provider class"""

    ROOT_URL = "https://apic-desktop.musixmatch.com/ws/1.1/"

    def __init__(self) -> None:
        super().__init__()
        self.token = None
        self.session.headers.update(
            {
                "authority": "apic-desktop.musixmatch.com",
                "cookie": "AWSELBCORS=0; AWSELB=0",
            }
        )

    async def _get(self, action: str, query: List[tuple]):
        if action != "token.get" and self.token is None:
            await self._get_token()
        query.append(("app_id", "web-desktop-app-v1.0"))
        if self.token is not None:
            query.append(("usertoken", self.token))
        t = str(int(time.time() * 1000))
        query.append(("t", t))
        url = self.ROOT_URL + action
        response = await self.session.get(url, params=query)
        return response

    async def _get_token(self):
        # Check if token is cached and not expired
        token_path = os.path.join(".syncedlyrics", "musixmatch_token.json")
        current_time = int(time.time())
        if os.path.exists(token_path):
            with open(token_path, "r") as token_file:
                cached_token_data = json.load(token_file)
            cached_token = cached_token_data.get("token")
            expiration_time = cached_token_data.get("expiration_time")
            if cached_token and expiration_time and current_time < expiration_time:
                self.token = cached_token
                return
        # Token not cached or expired, fetch a new token
        r = await self._get("token.get", [("user_language", "en")])
        d = json.loads(await r.text())
        if d["message"]["header"]["status_code"] == 401:
            time.sleep(10)
            return await self._get_token()
        new_token = d["message"]["body"]["user_token"]
        expiration_time = current_time + 600  # 10 minutes expiration
        # Cache the new token
        self.token = new_token
        token_data = {"token": new_token, "expiration_time": expiration_time}
        os.makedirs(".syncedlyrics", exist_ok=True)
        with open(token_path, "w") as token_file:
            json.dump(token_data, token_file)

    async def get_lrc_by_id(self, track_id: str) -> Optional[str]:
        r = await self._get(
            "track.subtitle.get", [("track_id", track_id), ("subtitle_format", "lrc")]
        )
        if not r.ok:
            return
        _json = json.loads(await r.text())
        body = _json["message"]["body"]

        if not body:
            return
        return body["subtitle"]["subtitle_body"]

    async def get_lrc(self, search_term: str, duration: int = -1, max_deviation: int = 2000) -> Tuple[Optional[str], int]:
        """Duration NotImplemented"""
        r = await self._get(
            "track.search",
            [
                ("q", search_term),
                ("page_size", "5"),
                ("page", "1"),
                ("s_track_rating", "desc"),
                ("quorum_factor", "1.0"),
            ],
        )

        _json = json.loads(await r.text())
        body = _json["message"]["body"]
        tracks = body["track_list"]

        tracks = sorted([(track, partial_ratio(search_term, track["track"]["track_name"])) for track in tracks], key=lambda x: x[1], reverse=True)
        if not tracks:
            return None
        return (await self.get_lrc_by_id(tracks[0][0]["track"]["track_id"]), tracks[0][1], 10000)
