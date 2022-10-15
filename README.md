# MediaUtility

Discord bot that aims to help with utility commands for songs, audio, and video.

Currently not particularly optimized for large scale usage, hence why I suggest
running it on a small scale for your own server(s).

## Commands

### `/shazam link`

Allows the user to find a song from a given piece of media online. Works for
anything that [YoutubeDL](https://github.com/yt-dlp/yt-dlp/) supports,
including generic links. The [ShazamIO](https://github.com/dotX12/ShazamIO)
project is used for the song finding backend.

`/shazam link https://www.youtube.com/watch?v=zoMYU_nOGNg 120`

This command will make the bot look for any songs at the 2 minute (120 second)
mark.

![An embed displaying the song information, including the album art.](https://i.imgur.com/UJcgHMo.png)

If it is a Youtube video, you may also use the built-in features of the `&t=`
query parameter to search at that point for songs. For instance, if you have a
long mix, you could give the bot a link at a certain timestamp and it would
search there, even if you don't explicitly provide a timestamp argument.

![An image showing Youtube's "share" function with the timestamp option ticked.](https://i.imgur.com/N2AMoTg.png)

### `/shazam file`

Works the exact same way as `/shazam link`, except you will be able to use your
own audio or video file to search from.

### `/extract`

Extracts the URL for a given piece of media. Currently only gets the "best"
preset from YoutubeDL, e.g., a high quality video & audio version of a YouTube
video, or the highest quality of audio available for a SoundCloud link.

`/extract https://twitter.com/Cloudflare/status/1580248328851316736`

This command will extract the media information from the Tweet, and if there is
a video it will then return that result to the user in an embed.

![An embed displaying CloudFlare's Twitter video.](https://i.imgur.com/984Ijoe.png)

## Hosting

If you are hosting this yourself you will need the following.

- Python 3.8+
  - `venv`
  - `pip`
- Redis
- Discord bot account

I won't cover creating a bot or inviting a bot to your server here.

You should run the following commands to install the bot and run it. These
commands assume you have Git installed, and that you are using a Debian based
operating system.

```bash
git clone https://github.com/ramadan8/MediaUtility
cd MediaUtility
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

From here you should create a `.env` file and populate it as so. Once it is
correctly filled out, type `source .env` to add the variables to your
environment.

```
# Your Redis instance's connection URI.
REDIS_HOST=redis://localhost

# Your Discord bot's token.
BOT_TOKEN=abcdefg1234

# Either 'prod' or 'dev'. Production will mean that individual guilds are not
# synced to immediately, instead pushing the commands globally to all guilds.
CMD_MODE=prod

# Any guilds you want to immediately sync to. Useful for development. This can
# also be left blank or discluded completely.
CMD_SYNC_GUILDS=1234,5678
```

Finally, to run the bot you may run `python3 -m src`.

### Docker

If you'd like to run this bot in a Docker environment you may refer to the
example [docker-compose.yml](./docker-compose.yml) file.

## Tests

If you'd like to run the tests you may type the following command.

```bash
python3 -m unittest
```

Again you will need Python 3.8 or above to run these tests as some are
asynchronous.
