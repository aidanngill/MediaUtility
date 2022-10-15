from typing import Optional

import discord
from discord import app_commands

from .. import shazam
from ..exceptions import InvalidLinkException


@app_commands.command(
    name="extract",
    description="Extract the media link from the given post."
)
@app_commands.rename(input_media="input")
@app_commands.describe(input_media="where to find the video/audio from.")
async def extract(interaction: discord.Interaction, input_media: str):
    await interaction.response.defer(thinking=True)

    try:
        data: Optional[dict] = await shazam.download_media(input_media, _format="best", download=False)
    except InvalidLinkException:
        return await interaction.edit_original_response(content="Please provide a valid link.")

    if not data:
        return await interaction.edit_original_response(content="Sorry, I couldn't find any media.")
    
    data_url = data.get("url")

    if not data_url:
        return await interaction.edit_original_response(content="Sorry, I couldn't find any media.")

    return await interaction.edit_original_response(content=f"Here is your [video]({data_url})! (sometimes videos don't embed, if not you'll have to download them yourself)")
