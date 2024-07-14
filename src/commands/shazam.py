from typing import Optional

import discord

from .. import shazam
from ..exceptions import InvalidLinkException
from typing import Optional

from discord import app_commands

async def cmd_shazam(
    interaction: discord.Interaction,
    input_link: str,
    time_start: Optional[int] = None,
    playlist_index: int = 1,
):
    await interaction.response.defer(thinking=True)

    try:
        song = await shazam.find_song(
            input_link, time_start, playlist_index=playlist_index
        )
    except InvalidLinkException:
        return await interaction.edit_original_response(
            content="Please provide a valid link."
        )

    if not song:
        return await interaction.edit_original_response(
            content="Sorry, I couldn't find any songs."
        )

    embed = discord.Embed()
    embed.set_thumbnail(url=song["album_art"])

    embed.add_field(name="Song", value=song["title"], inline=False)
    embed.add_field(name="Artist", value=song["artist"], inline=False)

    if song["album"]:
        embed.add_field(name="Album", value=song["album"], inline=False)

    if song["label"]:
        embed.add_field(name="Label", value=song["label"], inline=False)

    if song["release_year"]:
        embed.add_field(name="Released", value=song["release_year"], inline=False)

    await interaction.edit_original_response(embed=embed)

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

class ShazamGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="shazam", description="Find songs from media.")

shazam_group = ShazamGroup()
shazam_group.add_command(cmd_shazam_file)
shazam_group.add_command(cmd_shazam_link)
