"""
Search for an LRC format (synchronized lyrics) of a music.

```py
import syncedlyrics
lrc_text = syncedlyrics.search("[TRACK_NAME] [ARTIST_NAME]")
```
"""

import asyncio
from typing import Optional, List
import logging
from .providers import NetEase, Megalobiz, Musixmatch, Lrclib, Tencent
from .utils import is_lrc_valid, save_lrc_file

logger = logging.getLogger(__name__)


async def get_lrc_from_provider(provider, search_term, duration, allow_plain_format, max_deviation):
    logger.debug(f"Looking for an LRC on {provider.__class__.__name__}")
    result = await provider.get_lrc(search_term, duration=duration, max_deviation=max_deviation)

    if not result:
        return None
    lrc = result[0]
    if is_lrc_valid(lrc, allow_plain_format):
        logger.info(
            f'synced-lyrics found for "{search_term}" on {provider.__class__.__name__}'
        )
    return result


async def search(
    search_term: str,
    allow_plain_format: bool = False,
    save_path: str = None,
    providers: List[str] = None,
    duration: int = -1,
    max_deviation: int = 2000
) -> Optional[str]:
    """
    Returns the synced lyrics of the song in [LRC](https://en.wikipedia.org/wiki/LRC_(file_format)) format if found.
    ### Arguments
    - `search_term`: The search term to find the track
    - `allow_normal_format`: Return a plain text (not synced) lyrics if not LRC was found
    - `save_path`: Path to save `.lrc` lyrics. No saving if `None`
    - `providers`: A list of provider names to include in searching; loops over all the providers as soon as an LRC is found
    - `duration`: The duration of track in ms. Set below 0 if unknow
    - `max_deviation`: Max deviation for a subtitle length in ms, enable if duration is positive
    """
    _providers = [Musixmatch(), NetEase(), Megalobiz(), Lrclib(), Tencent()]
    if providers:
        # Filtering the providers
        _providers = [
            p for p in _providers if p.__class__.__name__ in providers]
    lrc = None
    tasks = [
        get_lrc_from_provider(provider, search_term, duration, allow_plain_format, max_deviation) for provider in _providers
    ]

    results = await asyncio.gather(*tasks)
    await _providers[0].session.close()

    results = [_ for _ in results if _]
    results = [_ for _ in results if _[0]]

    if results:
        if duration >= 0:
            lrc = sorted(results, key=lambda x: (x[1], -x[2]), reverse=True)[0][0]
        else:
            lrc = sorted(results, key=lambda x: (x[1],), reverse=True)[0][0]

    if not results:
        logger.info(f'No synced-lyrics found for "{search_term}" :(')
        return
    if save_path:
        save_path = save_path.format(search_term=search_term)
        save_lrc_file(save_path, lrc)
    return lrc
