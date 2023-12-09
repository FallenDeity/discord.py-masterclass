import asyncio
import datetime
import logging
import os
import time
import traceback
import typing
from gettext import gettext as _

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import GettextTranslator, SlashCommandTree


class CustomBot(commands.Bot):
    client: aiohttp.ClientSession
    _uptime: datetime.datetime

    def __init__(self, prefix: str, ext_dir: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(*args, **kwargs, command_prefix=commands.when_mentioned_or(prefix), intents=intents)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ext_dir = ext_dir
        self.synced = False

    async def _load_extensions(self) -> None:
        if not os.path.isdir(self.ext_dir):
            self.logger.error(f"Extension directory {self.ext_dir} does not exist.")
            return
        for filename in os.listdir(self.ext_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"{self.ext_dir}.{filename[:-3]}")
                    self.logger.info(f"Loaded extension {filename[:-3]}")
                except commands.ExtensionError:
                    self.logger.error(f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}")

    async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.logger.error(f"An error occurred in {event_method}.\n{traceback.format_exc()}")

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    async def _compile_translations(self) -> None:
        if self.tree.translator is None:
            return
        proc = await asyncio.create_subprocess_shell(
            "bash -c ./translations.sh", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        while True:
            line = await proc.stdout.readline() if proc.stdout else None
            if not line:
                break
            self.logger.info(line.decode().strip())
        await proc.wait()

    async def setup_hook(self) -> None:
        await self.tree.set_translator(GettextTranslator())
        self.client = aiohttp.ClientSession()
        await self._load_extensions()
        await self.load_extension("jishaku")
        if await self.tree._sync():
            self.logger.info("Command diff detected, generating new translations...")
            await self._compile_translations()
            await self.tree.smart_sync()
        self.logger.info("Synced command tree")
        self.loop.create_task(self.cog_watcher())
        self.logger.info("Started cog watcher")

    async def close(self) -> None:
        await super().close()
        await self.client.close()

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        load_dotenv()
        try:
            super().run(str(os.getenv("TOKEN")), *args, **kwargs)
        except (discord.LoginFailure, KeyboardInterrupt):
            self.logger.info("Exiting...")
            exit()

    async def cog_watcher(self) -> None:
        await self.wait_until_ready()
        self.logger.info("Watching for cog changes...")
        last = time.time()
        while True:
            extensions: set[str] = set()
            for name, module in self.extensions.items():
                if module.__file__ and os.stat(module.__file__).st_mtime > last:
                    extensions.add(name)
            reloaded = False
            for name in extensions:
                self.logger.info(f"Reloading extension {name}")
                try:
                    await self.reload_extension(name)
                    reloaded = True
                except commands.ExtensionError:
                    self.logger.error(f"Failed to reload extension {name}\n{traceback.format_exc()}")
            if reloaded:
                self.logger.info("Finished reloading extensions, syncing command tree...")
                await self._compile_translations()
                await self.tree.smart_sync()
                self.logger.info("Synced command tree")
            last = time.time()
            await asyncio.sleep(1)

    @property
    def tree(self) -> SlashCommandTree:
        return typing.cast(SlashCommandTree, super().tree)

    @property
    def user(self) -> discord.ClientUser:
        assert super().user, "Bot is not ready yet"
        return typing.cast(discord.ClientUser, super().user)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.utcnow() - self._uptime


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
    bot = CustomBot(prefix="!", ext_dir="cogs", tree_cls=SlashCommandTree, owner_ids={656838010532265994})

    @bot.tree.context_menu(name=_("user_ping"))
    async def ping_user(ctx: discord.Interaction, user: discord.User) -> None:
        await ctx.response.send_message(f"Pong! {user.mention}")

    bot.run()


if __name__ == "__main__":
    main()
