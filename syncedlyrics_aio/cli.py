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
        "-o", "--output", help="Path to save '.lrc' lyrics", default="{search_term}.lrc"
    )
    parser.add_argument(
        "--allow-plain",
        help="Return a plain text (not synced) lyrics if not LRC was found",
        action="store_true",
    )
    parser.add_argument(
        "-v", "--verbose", help="Use this flag to show the logs", action="store_true"
    )
    parser.add_argument(
        "-p", "--providers", help="Lrc providers", default=""
    )
    parser.add_argument(
        "-d", "--duration", help="The duration of track in ms. Set negative if unknow", type=int, default=-1
    )
    parser.add_argument(
        "-m", "--max_deviation", help="Max deviation for a subtitle length in ms, enable if duration is positive", type=int, default=2000
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    loop = asyncio.get_event_loop()
    lrc = loop.run_until_complete(search(args.search_term, args.allow_plain, args.output, args.providers.split(), args.duration, args.max_deviation))
    if lrc:
        print(lrc)
