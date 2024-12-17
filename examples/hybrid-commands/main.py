import datetime
import logging
import os
import traceback
import typing

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv


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
            owner_ids={656838010532265994},
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
        self.client = aiohttp.ClientSession()
        await self._load_extensions()
        await self.load_extension("jishaku")
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
    bot = CustomBot(prefix="!", ext_dir="cogs")

    @bot.group(name="factory")
    async def factory(ctx: commands.Context) -> None:
        """
        Factory commands.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command.

        Returns
        -------
        None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")

    @factory.command(name="create")
    async def create(ctx: commands.Context, name: str) -> None:
        """
        Create a factory.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command.
        name: str
            The name of the factory.

        Returns
        -------
        None
        """
        await ctx.send(f"Created factory {name}.")

    @factory.command(name="delete")
    async def delete(ctx: commands.Context, name: str) -> None:
        """
        Delete a factory.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command.
        name: str
            The name of the factory.

        Returns
        -------
        None
        """
        await ctx.send(f"Deleted factory {name}.")

    @factory.group(name="product")
    async def _product(ctx: commands.Context) -> None:
        """
        Product commands.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command.

        Returns
        -------
        None
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")
        bot.get_command()

    @_product.command(name="manufacture")
    async def manufacture(ctx: commands.Context, name: str, product: str) -> None:
        """
        Manufacture a product in a factory.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command.
        name: str
            The name of the factory.
        product: str
            The name of the product.

        Returns
        -------
        None
        """
        await ctx.send(f"Manufactured {product} in factory {name}.")

    @_product.command(name="sell")
    async def sell(ctx: commands.Context, name: str, product: str) -> None:
        """
        Sell a product from a factory.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command.
        name: str
            The name of the factory.
        product: str
            The name of the product.

        Returns
        -------
        None
        """
        await ctx.send(f"Sold {product} from factory {name}.")

    @bot.hybrid_command(name="echo")
    async def echo(ctx: commands.Context, *, message: str) -> None:
        """
        Repeat a message.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command.
        message: str
            The message to repeat.
        """
        await ctx.send(message)

    bot.run()


if __name__ == "__main__":
    main()
