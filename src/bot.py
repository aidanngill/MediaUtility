import logging
import os

import discord
from discord import app_commands

from .commands.extract import extract
from .commands.shazam import shazam_group

log = logging.getLogger(__name__)

GUILDS_SYNC = [
    discord.Object(id=int(g))
    for g in os.getenv("CMD_SYNC_GUILDS", "").split(",")
    if g != ""
]

class Client(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        mode = os.getenv("CMD_MODE", "dev")

        if mode not in ("dev", "prod"):
            mode = "dev"

        if mode == "dev":
            for guild in GUILDS_SYNC:
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)

        else:
            await self.tree.sync()

intents = discord.Intents.default()
bot = Client(intents=intents)

bot.tree.add_command(shazam_group)
bot.tree.add_command(extract)

@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")
