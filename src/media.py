from os import PathLike

import ffmpeg


def convert_video_to_gif(input_path: PathLike, output_path: PathLike) -> None:
    # fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse=dither=bayer"
    stream = ffmpeg.input(input_path).video

    split = (
        stream
            .filter("scale", 360, -1, flags="lanczos")
            .filter("fps", fps=15)
            .split()
    )

    (
        ffmpeg.filter(
            [
                split[1],
                split[0]
                    .filter("palettegen", max_colors=32)
            ],
            "paletteuse",
            dither="bayer"
        )
        .output(output_path)
        .overwrite_output()
        .run(quiet=True)
    )
