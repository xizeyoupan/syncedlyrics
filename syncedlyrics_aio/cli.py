import argparse
import logging
import asyncio
from syncedlyrics_aio import search


def cli_handler():
    """
    Console entry point handler function.
    This parses the CLI arguments passed to `syncedlyrics -OPTIONS` command
    """
    parser = argparse.ArgumentParser(
        description="Search for an LRC format (synchronized lyrics) of a music"
    )
    parser.add_argument("search_term", help="The search term to find the track.")
    parser.add_argument(
        "-p",
        help="Providers to include in the searching (separated by space). Default: all providers",
        default="",
        choices=["musixmatch", "lrclib", "netease", "megalobiz", "genius", "tencent"],
        nargs="+",
        type=str.lower,
    )
    parser.add_argument(
        "-l", "--lang", help="Language of the translation along with the lyrics"
    )
    parser.add_argument(
        "-o", "--output", help="Path to save '.lrc' lyrics", default="{search_term}.lrc"
    )
    parser.add_argument(
        "-v", "--verbose", help="Use this flag to show the logs", action="store_true"
    )
    parser.add_argument(
        "--plain-only",
        help="Only look for plain text (not synced) lyrics",
        action="store_true",
    )
    parser.add_argument(
        "--synced-only",
        help="Only look for synced lyrics",
        action="store_true",
    )
    parser.add_argument(
        "--enhanced",
        help="Returns word by word synced lyrics (if available)",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--duration",
        help="The duration of track in ms. Set to 0 if unknow",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-m",
        "--max_deviation",
        help="Max deviation of track in ms, enable if duration is set",
        type=int,
        default=5000,
    )
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    lrc = search(
        args.search_term,
        args.plain_only,
        args.synced_only,
        args.output,
        args.p,
        lang=args.lang,
        enhanced=args.enhanced,
    )

    loop = asyncio.get_event_loop()
    lrc = loop.run_until_complete(lrc)
    if lrc:
        print(lrc)
