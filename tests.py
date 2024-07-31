"""Some simple tests for geting notifed for API changes of the providers"""

import os
import syncedlyrics_aio
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)

q = os.getenv("TEST_Q", "bad guy billie eilish")
t = os.getenv("TEST_T", "-1")


async def _test_provider(provider: str, **kwargs):
    lrc = await syncedlyrics_aio.search(search_term=q, providers=[provider], **kwargs)
    logging.debug("\n" + lrc)
    assert isinstance(lrc, str)
    return lrc


async def test_netease():
    await _test_provider("NetEase")


# async def test_netease_with_duration():
#     await _test_provider("NetEase", duration=256000)


async def test_musixmatch():
    await _test_provider("Musixmatch")


async def test_musixmatch_translation():
    lrc = await _test_provider("Musixmatch", lang="es")
    # not only testing there is a result, but the translation is also included
    assert syncedlyrics_aio.utils.has_translation(lrc)


async def test_musixmatch_enhanced():
    await _test_provider("Musixmatch", enhanced=True)


async def test_lrclib():
    await _test_provider("Lrclib")


async def test_genius():
    await _test_provider("Genius")


async def test_tencent():
    await _test_provider("Tencent")


# async def test_tencent_with_duration():
#     await _test_provider("Tencent", duration=256000)


async def test_plaintext_only():
    lrc = await _test_provider("Lrclib", plain_only=True)
    assert syncedlyrics_aio.utils.identify_lyrics_type(lrc) == "plaintext"


async def test_synced_only():
    lrc = await _test_provider("Lrclib", synced_only=True)
    assert syncedlyrics_aio.utils.identify_lyrics_type(lrc) == "synced"


# Not working (at least temporarily)
# async def test_deezer():
#     _test_provider("Deezer")


# Fails randomly on CI
# async def test_megalobiz():
#     await _test_provider("Megalobiz")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_genius())
