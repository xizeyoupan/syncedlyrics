"""Utility functions for `syncedlyrics` package"""

import re
from bs4 import BeautifulSoup, FeatureNotFound


def is_lrc_valid(lrc: str, allow_plain_format: bool = False) -> bool:
    """Checks whether a given LRC string is valid or not."""
    if not lrc:
        return False
    if not allow_plain_format:
        if not ("[" in lrc and "]" in lrc):
            return False

    return True


def save_lrc_file(path: str, lrc_text: str):
    """Saves the `.lrc` file"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(lrc_text)


async def generate_bs4_soup(session, url: str, **kwargs):
    """Returns a `BeautifulSoup` from the given `url`.
    Tries to use `lxml` as the parser if available, otherwise `html.parser`
    """
    r = await session.get(url)
    text = await r.text()
    try:
        soup = BeautifulSoup(text, features="lxml", **kwargs)
    except FeatureNotFound:
        soup = BeautifulSoup(text, features="html.parser", **kwargs)
    return soup


def trim_lyric(lyric):
    result = []
    lines = lyric.split('\n')
    for line in lines:
        match = re.match(r'^\[(\d{2}):(\d{2}\.\d*)\](.*)$', line)
        if match:
            result.append({
                'time': int(int(match[1]) * 60 * 1000 + float(match[2]) * 1000),
                'text': match[3]
            })
    return sorted(result, key=lambda x: x['time'])


def format_lyrics(lyric, tlyric):
    lyric_array = trim_lyric(lyric)
    tlyric_array = trim_lyric(tlyric)

    if len(tlyric_array) == 0:
        return lyric

    result = []
    j = 0

    for i in range(len(lyric_array)):
        if j == len(tlyric_array):
            break

        time = lyric_array[i]['time']
        text = lyric_array[i]['text']

        while time > tlyric_array[j]['time'] and j + 1 < len(tlyric_array):
            j += 1

        if time == tlyric_array[j]['time'] and len(tlyric_array[j]['text']) > 0:
            text = f"{text} ({tlyric_array[j]['text']})"

        result.append({
            'time': time,
            'text': text
        })

    formatted_result = []

    for x in result:
        minus = str(x['time'] // 60000).zfill(2)
        second = str((x['time'] % 60000) // 1000).zfill(2)
        millisecond = str(x['time'] % 1000).zfill(3)

        formatted_result.append(f"[{minus}:{second}.{millisecond}]{x['text']}")

    return '\n'.join(formatted_result)
