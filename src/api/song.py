from typing import Optional, TypedDict


class Song(TypedDict):
    title: str
    artist: str
    album: Optional[str]
    album_art: Optional[str]
    label: Optional[str]
    release_year: Optional[str]

def create(data: dict) -> Optional[Song]:
    """ Takes input data from the Shazam API and tries to turn it into a song. """
    if not data.get("track"):
        return

    data_track: dict = data["track"]

    def _find_album_art():
        data_images: dict = data_track.get("images", {})

        for key in ["coverarthq", "coverart", "background"]:
            if data_images.get(key):
                return data_images[key]
    
    def _find_section_data(key: str) -> Optional[str]:
        data_sections: list = data_track.get("sections", [])

        for section in data_sections:
            if section["type"] == "SONG":
                for item in section["metadata"]:
                    if item["title"] == key:
                        return item["text"]
    
    return Song(
        title=data_track["title"],
        artist=data_track["subtitle"],
        album=_find_section_data("Album"),
        album_art=_find_album_art(),
        label=_find_section_data("Label"),
        release_year=_find_section_data("Release")
    )
