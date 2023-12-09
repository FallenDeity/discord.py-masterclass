from __future__ import annotations

import datetime
import typing
from gettext import gettext as _

import discord
from discord import app_commands
from discord.ext import commands

if typing.TYPE_CHECKING:
    from .. import CustomBot


def is_owner():
    async def predicate(inter: discord.Interaction) -> bool:
        return inter.user.id == 1234567890

    return app_commands.check(predicate)


class DurationConverter(app_commands.Transformer):
    async def transform(self, inter: discord.Interaction, argument: str) -> datetime.timedelta:
        multipliers = {
            "s": 1,  # seconds
            "m": 60,  # minutes
            "h": 3600,  # hours
            "d": 86400,  # days
            "w": 604800,  # weeks
        }
        try:
            amount = int(argument[:-1])
            unit = argument[-1]
            seconds = amount * multipliers[unit]
            delta = datetime.timedelta(seconds=seconds)
            return delta
        except (ValueError, KeyError):
            raise commands.BadArgument("Invalid duration provided.")


class General(commands.Cog):
    group = app_commands.Group(name=_("utility"), description=_("Utility commands"))

    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot

    @group.command(name=_("duration"), description=_("Convert a duration to a timedelta"))
    @is_owner()
    async def duration(
        self, inter: discord.Interaction, duration: app_commands.Transform[datetime.timedelta, DurationConverter]
    ) -> None:
        await inter.response.send_message(f"Duration: {duration}")

    @group.command(name=_("ping"), description=_("Get the bot's latency"))
    async def ping(self, inter: discord.Interaction) -> None:
        await inter.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name=_("echo"), description=_("Echo a message"), extras={"params": (_("message"),)})
    async def echo(self, inter: discord.Interaction, message: str) -> None:
        await inter.response.send_message(message)

    @app_commands.command(name=_("info"), description=_("Get info about a user"), extras={"params": (_("user"),)})
    async def info(self, inter: discord.Interaction, user: discord.User) -> None:
        await inter.response.send_message(f"User: {user}")

    @commands.hybrid_command(name=_("tell"), description=_("Tell a message"), extras={"params": (_("message"),)})
    @app_commands.choices(
        message=[
            app_commands.Choice(name=_("hello"), value="Hello!"),
            app_commands.Choice(name=_("goodbye"), value="Goodbye!"),
            app_commands.Choice(name=_("how are you?"), value="I'm doing well, thanks!"),
        ]
    )
    async def say(self, ctx: commands.Context[CustomBot], message: str) -> None:
        await ctx.send(message)


async def setup(bot: CustomBot) -> None:
    await bot.add_cog(General(bot))
