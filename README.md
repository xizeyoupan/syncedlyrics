# syncedlyrics_aio
 Get an LRC format (synchronized) lyrics for your music **with aiohttp support**.
 
 [![Downloads](https://static.pepy.tech/badge/syncedlyrics_aio/month)](https://pepy.tech/project/syncedlyrics_aio)

## Installation
```
pip install syncedlyrics_aio
```
## Usage
### CLI
```
syncedlyrics_aio "SEARCH_TERM"
```

By default, this will prefer time synced lyrics, but use plaintext lyrics, if no synced lyrics are available.
To only allow one type of lyrics specify `--plain-only` or `--synced-only` respectively.

#### Available Options
| Flag            | Description                                                                                                                                                                                   |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-o`            | Path to save `.lrc` lyrics, default="{search_term}.lrc"                                                                                                                                       |
| `-p`            | Space-separated list of [providers](#providers) to include in searching                                                                                                                       |
| `-l`            | Language code of the translation ([ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes) format)                                                                           |
| `-v`            | Use this flag to show the logs                                                                                                                                                                |
| `--plain-only`  | Only look for plain text (not synced) lyrics                                                                                                                                                  |
| `--synced-only` | Only look for synced lyrics                                                                                                                                                                   |
| `--enhanced`    | Searches for an [Enhanced](https://en.wikipedia.org/wiki/LRC_(file_format)#A2_extension:_word_time_tag) (word-level karaoke) format. If it isn't available, search for regular synced lyrics. |
| `-d`            | The duration of track in ms. Keep default if unknow. Only for netease and tencent                                                                                                                                           |
| `-m`            | Max deviation for lyrics in ms, ignore if duration is default                                                                                                                                 |

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
syncedlyrics_aio.search("...", plain_only=True, save_path="{search_term}_1234.lrc", providers=["NetEase"], duration=213000)
```

## Providers
- [Musixmatch](https://www.musixmatch.com/)
- ~~[Deezer](https://deezer.com/)~~ (Currently not working anymore)
- [Lrclib](https://github.com/tranxuanthang/lrcget/issues/2#issuecomment-1326925928)
- [NetEase](https://music.163.com/)
- [Megalobiz](https://www.megalobiz.com/)
- [Genius](https://genius.com) (For plain format)
- ~~[Lyricsify](https://www.lyricsify.com/)~~ (Broken duo to Cloudflare protection)
- [Tencent](https://y.qq.com/)

Feel free to suggest more providers or make PRs to fix the broken ones.

## License
[MIT](https://github.com/rtcq/syncedlyrics/blob/master/LICENSE)

## Citation
If you use this library in your research, you can cite as follows:
```
@misc{syncedlyrics,
  author = {Momeni, Mohammad},
  title = {syncedlyrics},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/moehmeni/syncedlyrics}},
}
```
