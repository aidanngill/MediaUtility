import os

import ffmpeg


def video_to_gif(input_path: str, output_path: str) -> None:
    """Tries to convert a given video to a GIF and compresses it.

    Args:
        input_path (str): Path to the media we should use as an input.
        output_path (str): Path to save the output media to.

    Returns:
        None.
    """

    # 360px width, automatically configure height, and cap to 15 FPS.
    split = (
        ffmpeg.input(input_path)
        .video.filter("scale", 360, -1, flags="lanczos")
        .filter("fps", fps=15)
        .split()
    )

    (
        ffmpeg.filter(
            [split[1], split[0].filter("palettegen", max_colors=32)],
            "paletteuse",
            dither="bayer",
        )
        .output(output_path)
        .overwrite_output()
        .run(quiet=True)
    )


def video(input_path: str, output_path: str) -> None:
    """Tries to convert the input video into the format specified by the
    extension of the output path.

    For instance, converting `input.mp4` to `output.webm` would convert the
    MP4 video into a WebM video.

    Args:
        input_path (str): Path to the media we should use as an input.
        output_path (str): Path to save the output media to.

    Returns:
        None.
    """
    _, extension = os.path.splitext(output_path)

    if extension == ".gif":
        return video_to_gif(input_path, output_path)

    (ffmpeg.input(input_path).output(output_path).run(quiet=True))
