from typing import Optional

import discord

from ... import shazam
from ...exceptions import InvalidLinkException


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
