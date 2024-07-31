"""Utility functions for `syncedlyrics` package"""

from dataclasses import dataclass
from bs4 import BeautifulSoup, FeatureNotFound
import rapidfuzz
from typing import Union, Callable, Optional
import datetime
from enum import Enum, auto
import re
import os
from pathlib import Path

R_FEAT = re.compile(r"\((feat.+)\)", re.IGNORECASE)


class TargetType(Enum):
    PLAINTEXT = auto()
    PREFER_SYNCED = auto()
    SYNCED_ONLY = auto()


@dataclass
class Lyrics:
    synced: Optional[str] = None
    unsynced: Optional[str] = None

    def add_unknown(self, unknown: str):
        type = identify_lyrics_type(unknown)
        if type == "synced":
            self.synced = unknown
        elif type == "plaintext":
            self.unsynced = unknown

    def update(self, other: Optional["Lyrics"]):
        if not other:
            return
        if other.synced:
            self.synced = other.synced
        if other.unsynced:
            self.unsynced = other.unsynced

    def is_preferred(self, target_type: TargetType) -> bool:
        return bool(
            self.synced or (target_type == TargetType.PLAINTEXT and self.unsynced)
        )

    def is_acceptable(self, target_type: TargetType) -> bool:
        return bool(
            self.synced or (target_type != TargetType.SYNCED_ONLY and self.unsynced)
        )

    def to_str(self, target_type: TargetType) -> str:
        if target_type == TargetType.PLAINTEXT:
            return self.unsynced or synced_to_plaintext(self.synced)
        elif target_type == TargetType.PREFER_SYNCED:
            return self.synced or self.unsynced
        return self.synced

    def save_lrc_file(self, path: str, target_type: TargetType):
        """Saves the `.lrc` file"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_str(target_type))


def get_cache_path(lib_name: str = "syncedlyrics", auto_create: bool = True) -> Path:
    """Get or create a cache directory for the given library name."""
    if os.name == "nt":  # Windows
        base_dir = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
    elif os.name == "posix":
        if "Darwin" in os.uname().sysname:  # macOS
            base_dir = os.path.expanduser("~/Library/Caches")
        else:  # Linux
            base_dir = os.path.expanduser("~/.cache")
    else:
        base_dir = os.path.expanduser("~")
    target_dir = Path(base_dir) / lib_name
    if auto_create:
        target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def synced_to_plaintext(synced_lyrics: str) -> str:
    return re.sub(r"\[\d+:\d+\.\d+\] ", "", synced_lyrics)


def identify_lyrics_type(lrc: str) -> str:
    """Identifies the type of the LRC string"""
    if not lrc:
        return "invalid"
    lines = lrc.split("\n")[5:10]
    if all("[" in l for l in lines):
        return "synced"
    return "plaintext"


def has_translation(lrc: str) -> bool:
    """Checks whether the LRC string has a translation or not"""
    lines = lrc.split("\n")[5:10]
    for i, line in enumerate(lines):
        if "[" in line:
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if "(" not in next_line:
                    return False
    return True


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


def format_time(time_in_seconds: float):
    """Returns a [mm:ss.xx] formatted string from the given time in seconds."""
    time = datetime.timedelta(seconds=time_in_seconds)
    minutes, seconds = divmod(time.seconds, 60)
    return f"{minutes:02}:{seconds:02}.{time.microseconds//10000:02}"


def str_score(a: str, b: str) -> float:
    """Returns the similarity score of the two strings"""
    # if user does not specify any "feat" in the search term,
    # remove the "feat" from the search results' names
    a, b = a.lower(), b.lower()
    if "feat" not in b:
        a, b = R_FEAT.sub("", a), R_FEAT.sub("", b)
    return rapidfuzz.fuzz.partial_ratio(a, b)


def str_same(a: str, b: str, n: int) -> bool:
    """Returns `True` if the similarity score of the two strings is greater than `n`"""
    return round(str_score(a, b)) >= n


def sort_results(
    results: list,
    search_term: str,
    compare_key: Union[str, Callable[[dict], str]] = "name",
) -> list:
    """
    Sorts the API results based on the similarity score of the `compare_key` with
    the `search_term`.

    ## Parameters
    - `results`: The API results
    - `search_term`: The search term
    - `compare_key`: The key to compare the `search_term` with. Can be a string or a
    function that takes a track and returns a string.
    """
    if isinstance(compare_key, str):

        def compare_key(t):
            return t[compare_key]

    def sort_key(t):
        return str_score(compare_key(t), search_term)

    return sorted(results, key=sort_key, reverse=True)


def get_best_match(
    results: list,
    search_term: str,
    compare_key: Union[str, Callable[[dict], str]] = "name",
    min_score: int = 65,
) -> Optional[dict]:
    """
    Returns the best match from the API results based on the similarity score of the `compare_key`
    with the `search_term`.
    """
    if not results:
        return None
    results = sort_results(results, search_term, compare_key=compare_key)
    best_match = results[0]

    value_to_compare = (
        best_match[compare_key]
        if isinstance(compare_key, str)
        else compare_key(best_match)
    )
    if not str_same(value_to_compare, search_term, n=min_score):
        return None
    return best_match


def trim_lyric(lyric):
    result = []
    lines = lyric.split("\n")
    for line in lines:
        match = re.match(r"^\[(\d{2}):(\d{2}\.\d*)\](.*)$", line)
        if match:
            result.append(
                {
                    "time": int(int(match[1]) * 60 * 1000 + float(match[2]) * 1000),
                    "text": match[3],
                }
            )
    return sorted(result, key=lambda x: x["time"])


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

        time = lyric_array[i]["time"]
        text = lyric_array[i]["text"]

        while time > tlyric_array[j]["time"] and j + 1 < len(tlyric_array):
            j += 1

        if time == tlyric_array[j]["time"] and len(tlyric_array[j]["text"]) > 0:
            text = f"{text} ({tlyric_array[j]['text']})"

        result.append({"time": time, "text": text})

    formatted_result = []

    for x in result:
        minus = str(x["time"] // 60000).zfill(2)
        second = str((x["time"] % 60000) // 1000).zfill(2)
        millisecond = str(x["time"] % 1000).zfill(3)

        formatted_result.append(f"[{minus}:{second}.{millisecond}]{x['text']}")

    return "\n".join(formatted_result)
