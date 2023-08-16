"""Some simple tests for geting notifed for API changes of the providers"""

import os
import asyncio
from syncedlyrics_aio import search
import pytest

q = os.getenv("TEST_Q", "bad guy billie eilish")
t = os.getenv("TEST_T", "-1")


async def _test_provider(provider: str):
    lrc = await search(q, allow_plain_format=True, duration=int(t), providers=[provider])
    print(lrc)
    assert isinstance(lrc, (str, type(None)))


@pytest.mark.asyncio
async def test_netease():
    await _test_provider("NetEase")


@pytest.mark.asyncio
async def test_megalobiz():
    await _test_provider("Megalobiz")


@pytest.mark.asyncio
async def test_musixmatch():
    await _test_provider("Musixmatch")


@pytest.mark.asyncio
async def test_lrclib():
    await _test_provider("Lrclib")


@pytest.mark.asyncio
async def test_tencent():
    await _test_provider("Tencent")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_tencent())
