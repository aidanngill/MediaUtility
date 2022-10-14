from discord import app_commands

from .file import cmd_shazam_file
from .link import cmd_shazam_link


class ShazamGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="shazam", description="find songs from media.")


shazam_group = ShazamGroup()
shazam_group.add_command(cmd_shazam_file)
shazam_group.add_command(cmd_shazam_link)
