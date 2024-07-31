"""
Search for an LRC format (synchronized lyrics) of a music.

```py
import syncedlyrics_aio

loop = asyncio.get_event_loop()
lrc = loop.run_until_complete(syncedlyrics_aio.search("[TRACK_NAME] [ARTIST_NAME]"))
if lrc:
    print(lrc)
```
"""

import asyncio
from typing import Optional, List
import traceback
import logging
from .providers import Deezer, Lrclib, Musixmatch, NetEase, Megalobiz, Genius, Tencent
from .utils import Lyrics, TargetType
from .providers.base import LRCProvider

logger = logging.getLogger(__name__)


async def search(
    search_term: str,
    plain_only: bool = False,
    synced_only: bool = False,
    save_path: Optional[str] = None,
    providers: List[str] = [],
    lang: Optional[str] = None,
    enhanced: bool = False,
    duration: int = 0,
    max_deviation: int = 5000,
) -> Optional[str]:
    """
    Returns the synced lyrics of the song in [LRC](https://en.wikipedia.org/wiki/LRC_(file_format)) format if found.
    ### Arguments
    - `search_term`: The search term to find the track
    - `plain_only`: Only look for plain text (not synced) lyrics
    - `synced_only`: Only look for synced lyrics
    - `save_path`: Path to save `.lrc` lyrics. No saving if `None`
    - `providers`: A list of provider names to include in searching; loops over all the providers as soon as an LRC is found
    - `lang`: Language of the translation along with the lyrics. **Only supported by Musixmatch**
    - `enhanced`: Returns word by word synced lyrics if available. **Only supported by Musixmatch**
    - `duration`: The duration of track in ms, if the provider supports. Keep default if unknow
    - `max_deviation`: Max deviation of track in ms, enable if duration is set, defalut is 2000
    """
    if plain_only and synced_only:
        logger.error(
            "--plaintext-only and --synced-only flags cannot be used together."
        )
        return None

    target_type = TargetType.PREFER_SYNCED
    if plain_only:
        target_type = TargetType.PLAINTEXT
    elif synced_only:
        target_type = TargetType.SYNCED_ONLY
    lrc = Lyrics()

    _providers = [
        Musixmatch(lang=lang, enhanced=enhanced),
        Lrclib(),
        # Deezer(),
        NetEase(duration=duration, max_deviation=max_deviation),
        Megalobiz(),
        Genius(),
        Tencent(duration=duration, max_deviation=max_deviation),
    ]

    tasks = []

    async def get_lrc_from_provider(provider):
        logger.debug(f"Looking for an LRC on {provider}")
        try:
            return await provider.get_lrc(search_term)
        except Exception as e:
            logger.error(f"An error occurred while searching for an LRC on {provider}")
            logger.error(e)
            traceback.print_exc()
            if lang:
                logger.error("Aborting, since `lang` is only supported by Musixmatch")
                return None
        if lrc.is_preferred(target_type):
            logger.info(f'Lyrics found for "{search_term}" on {provider}')
        elif lrc.is_acceptable(target_type):
            logger.info(
                f"Found plaintext lyrics on {provider}, but continuing search for synced lyrics"
            )
        else:
            logger.debug(
                f"No suitable lyrics found on {provider}, continuing search..."
            )

    for provider in _select_providers(_providers, providers):
        tasks.append(get_lrc_from_provider(provider))

    results = await asyncio.gather(*tasks)
    for lyrics in results:
        lrc.update(lyrics)

    if not lrc.is_acceptable(target_type):
        logger.info(f'No suitable lyrics found for "{search_term}" :(')
        return None
    if save_path:
        save_path = save_path.format(search_term=search_term)
        lrc.save_lrc_file(save_path, target_type)
    return lrc.to_str(target_type)


def _select_providers(
    providers: List[LRCProvider], string_list: List[str]
) -> List[LRCProvider]:
    """
    Returns a list of provider classes based on the given string list.
    """
    strings_lowercase = [p.lower() for p in string_list]
    selection = [p for p in providers if str(p).lower() in strings_lowercase]
    if not selection:
        if string_list:
            # List of providers specified but not found.
            # Deliberately returning nothing instead of all to avoid unexpected behaviour.
            logger.error(
                f"Providers {string_list} not found in the list of available providers."
            )
            return []
        else:
            # No providers specified, using all
            return providers
    return selection
