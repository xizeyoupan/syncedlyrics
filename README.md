# syncedlyrics
 Get an LRC format (synchronized) lyrics for your music.
 
 [![Downloads](https://static.pepy.tech/badge/syncedlyrics_aio/month)](https://pepy.tech/project/syncedlyrics_aio)

## Installation
```
pip install syncedlyrics_aio
```
## Usage
### CLI
```
syncedlyrics "SEARCH_TERM"
```
#### Available Options
| Flag            | Description                                                          |
| --------------- | -------------------------------------------------------------------- |
| `-o`            | Path to save `.lrc` lyrics, default="{search_term}.lrc"              |
| `-v`            | Use this flag to show the logs                                       |
| `--allow-plain` | Return a plain text (not synced) lyrics if no LRC format was found   |
| `-p`            | Lrc providers, split by whitespaces                                  |
| `-d`            | The duration of track in ms. Keep default if unknow                  |
| `-m`            | Max deviation for a subtitle length in ms, enable if duration is set |

### Python
```py
import syncedlyrics_aio

loop = asyncio.get_event_loop()
lrc = loop.run_until_complete(syncedlyrics_aio.search("[TRACK_NAME] [ARTIST_NAME]"))
if lrc:
    print(lrc)
```
Or with options:
```py
syncedlyrics_aio.search("...", allow_plain_format=True, save_path="{search_term}_1234.lrc", providers=["NetEase"], duration=213000)
```

## Providers
- [Musixmatch](https://www.musixmatch.com/)
- [Lyricsify](https://www.lyricsify.com/)
- [NetEase](https://music.163.com/)
- [Megalobiz](https://www.megalobiz.com/)
- ~~[Deezer](https://deezer.com/)~~ (Currently broken, PR is appreciated)

Feel free to suggest more providers please.

## License
[MIT](https://github.com/rtcq/syncedlyrics/blob/master/LICENSE)
