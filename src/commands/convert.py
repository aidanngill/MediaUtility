import asyncio
import os
from tempfile import TemporaryDirectory

import discord
import ffmpeg
from discord import Enum, app_commands

from .. import media, shazam


class Formats(Enum):
    # audio
    mp3 = "mp3"
    flac = "flac"

    # video
    mp4 = "mp4"
    webm = "webm"
    gif = "gif"

@app_commands.command(
    name="convert",
    description="Convert a video or piece of audio to another format."
)
@app_commands.rename(
    input_media="input",
    new_format="format"
)
@app_commands.describe(
    input_media="where to find the video/audio from.",
    new_format="which extension the converted media should use."
)
async def convert(
    interaction: discord.Interaction,
    input_media: discord.Attachment,
    new_format: Formats,
):
    await interaction.response.defer(thinking=True)

    loop = asyncio.get_event_loop()

    with TemporaryDirectory() as path_temp:
        file_in = os.path.join(path_temp, input_media.filename)
        file_out = os.path.join(path_temp, f"bawt.{new_format.value}")

        await shazam.download_file(input_media.url, file_in)

        def _convert_media():
            if new_format != Formats.gif:
                ffmpeg \
                    .input(file_in) \
                    .output(file_out) \
                    .run(quiet=True)
            else:
                media.convert_video_to_gif(file_in, file_out)
        
        await loop.run_in_executor(None, lambda: _convert_media())

        try:
            await interaction.edit_original_response(attachments=[discord.File(file_out)])
        except discord.HTTPException as e:
            if e.status == 413:
                await interaction.edit_original_response(content="Sorry, the file generated was too large.")
