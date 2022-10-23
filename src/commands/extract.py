import os
from tempfile import TemporaryDirectory
from typing import Optional

import discord
from discord import app_commands

from .. import shazam
from ..exceptions import InvalidLinkException


@app_commands.command(
    name="extract", description="Extract the media link from the given post."
)
@app_commands.rename(input_media="input", playlist_item="index")
@app_commands.describe(
    input_media="where to find the video/audio from.",
    playlist_item="which index to download from a playlist.",
)
async def extract(
    interaction: discord.Interaction, input_media: str, playlist_item: int = 1
):
    await interaction.response.defer(thinking=True)

    try:
        data: Optional[dict] = await shazam.download_media(
            input_media, index=playlist_item, download=False
        )
    except InvalidLinkException:
        return await interaction.edit_original_response(
            content="Please provide a valid link."
        )

    if not data:
        return await interaction.edit_original_response(
            content="Sorry, I couldn't find any media."
        )

    extractor: str = data.get("extractor", "").lower()

    # If we have a Reddit, Instagram, or TikTok video, download it ourself and send it
    # as an attachment.
    # - Reddit splits their videos into audio and video. We will need to
    #   re-combine it by ourselves.
    # - Instagram and Tiktok have slow CDNs and usually lower quality/shorter
    #   videos, so quickly downloading them and re-uploading is worth it for
    #   Discord's comparatively quick CDN.
    if extractor in ("reddit", "instagram", "tiktok"):
        # TODO: Windows spits out an error about the file being used by another program
        # when this context manager exits. Doesn't affect anything, just means that
        # temporary stuff won't be deleted. Still annoying.
        with TemporaryDirectory() as path_temp:
            file_name = f"{data['extractor']} - {data['id']}.{data.get('ext', 'mp4')}"
            file_path = os.path.join(path_temp, file_name)

            await shazam.download_media(input_media, file_path)

            attachments = [discord.File(file_path)]

            await interaction.edit_original_response(attachments=attachments)

    # Send the raw URL otherwise.
    else:
        # TODO: Maybe cache the URL result, hash the given URL or something.
        message = (
            f"Here is your [video]({data.get('url')})! "
            "(sometimes video don't embed, if not you'll have to download them)"
        )

        await interaction.edit_original_response(content=message)
