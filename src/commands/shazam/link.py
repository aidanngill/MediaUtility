from typing import Optional

import discord
from discord import app_commands

from .base import cmd_shazam


@app_commands.command(name="link", description="Try to find a song from the link.")
@app_commands.rename(input_media="input", time_start="time", playlist_index="index")
@app_commands.describe(
    input_media="where to find the video/audio from.",
    time_start="which timestamp to search from.",
    playlist_index="which index to download from a playlist.",
)
async def cmd_shazam_link(
    interaction: discord.Interaction,
    input_media: str,
    time_start: Optional[int] = None,
    playlist_index: int = 1,
):
    return await cmd_shazam(interaction, input_media, time_start, playlist_index)
