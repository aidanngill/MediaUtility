from typing import Optional

import discord
from discord import app_commands

from .base import cmd_shazam


@app_commands.command(
    name="file", description="Try to find a song from the attachment."
)
@app_commands.rename(input_media="input", time_start="time")
@app_commands.describe(
    input_media="where to find the video/audio from.",
    time_start="which timestamp to search from.",
)
async def cmd_shazam_file(
    interaction: discord.Interaction,
    input_media: discord.Attachment,
    time_start: Optional[int] = None,
):
    return await cmd_shazam(interaction, input_media.url, time_start)
