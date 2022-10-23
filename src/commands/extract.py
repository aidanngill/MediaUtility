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
@app_commands.rename(input_media="input", playlist_index="index")
@app_commands.describe(
    input_media="where to find the video/audio from.",
    playlist_index="which index to download from a playlist.",
)
async def extract(
    interaction: discord.Interaction, input_media: str, playlist_index: int = 1
):
    await interaction.response.defer(thinking=True)

    try:
        data: Optional[dict] = await shazam.download_media(
            input_media, playlist_index=playlist_index, should_download=False
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
            file_path = os.path.join(
                path_temp,
                "{0} - {1}.{2}".format(
                    data["extractor"], data["id"], data.get("ext", "mp4")
                ),
            )

            # TODO: Issue with (at least) Instagram where there are mixed video/image
            # slides. E.g., if a picture is first, and a video is second, the desired
            # command is `/extract <link> 2`, but instead only the videos are detected
            # and you will end up having to type `1` as the index.
            await shazam.download_media(
                input_media,
                output_path=file_path,
                playlist_index=playlist_index,
                should_download=True,
            )

            # Validate that the file was downloaded successfully.
            if os.path.exists(file_path):
                await interaction.edit_original_response(
                    attachments=[discord.File(file_path)]
                )
            else:
                await interaction.edit_original_response(
                    content="Sorry, I couldn't download the requested media right now. "
                    "Maybe try again later."
                )

    # Send the raw URL otherwise.
    else:
        # TODO: Maybe cache the URL result, hash the given URL or something.
        message = (
            f"Here is your [video]({data.get('url')})! "
            "(sometimes video don't embed, if not you'll have to download them)"
        )

        await interaction.edit_original_response(content=message)
