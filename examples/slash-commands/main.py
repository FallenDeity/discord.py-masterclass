import datetime
import logging
import os
import traceback
import typing

import aiohttp
import discord
from discord import app_commands
from discord.app_commands import locale_str as _
from discord.ext import commands
from dotenv import load_dotenv
from utils.help import CustomHelpCommand
from utils.tree import SlashCommandTree


class CustomBot(commands.Bot):
    client: aiohttp.ClientSession
    _uptime: datetime.datetime

    def __init__(self, prefix: str, ext_dir: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(
            *args,
            **kwargs,
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
            help_command=None,
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ext_dir = ext_dir
        self.synced = True

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

    async def setup_hook(self) -> None:
        # await self.tree.set_translator(Translator())
        self.client = aiohttp.ClientSession()
        await self._load_extensions()
        if not self.synced:
            await self.tree.sync()
            self.synced = not self.synced
            self.logger.info("Synced command tree")

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

    @property
    def user(self) -> discord.ClientUser:
        assert super().user, "Bot is not ready yet"
        return typing.cast(discord.ClientUser, super().user)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.utcnow() - self._uptime


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
    bot = CustomBot(prefix="!", ext_dir="cogs", tree_cls=SlashCommandTree)

    @bot.tree.command(name=_("test"), description=_("A test command"))
    @app_commands.choices(
        test=[
            app_commands.Choice(name=_("One"), value=1),
            app_commands.Choice(name=_("Two"), value=2),
            app_commands.Choice(name=_("Three"), value=3),
        ]
    )
    @app_commands.describe(test=_("A test choice"))
    async def translations(interaction: discord.Interaction, test: app_commands.Choice[int]) -> None:
        await interaction.response.send_message(repr(test))

    @bot.hybrid_command(name="help", description="Show help for a command")
    async def help_(ctx: commands.Context, command: str = None) -> None:
        help_command = CustomHelpCommand(include_app_commands=True)
        help_command.context = ctx
        await help_command.command_callback(ctx, command=command)

    bot.run()


if __name__ == "__main__":
    main()
