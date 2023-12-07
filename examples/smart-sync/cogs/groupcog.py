from __future__ import annotations

import typing
from gettext import gettext as _

import discord
from discord import app_commands
from discord.ext import commands

if typing.TYPE_CHECKING:
    from .. import CustomBot


class MathGroup(commands.GroupCog, name=_("math"), description=_("Math commands")):
    group = app_commands.Group(name=_("functions"), description=_("Math functions"))

    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot
        super().__init__()

    @group.command(name=_("pow"), description=_("Raise a number to a power"))
    async def power(self, inter: discord.Interaction, a: int, b: int) -> None:
        await inter.response.send_message(f"{a} ^ {b} = {a ** b}")

    @group.command(name=_("sqrt"), description=_("Get the square root of a number"))
    async def sqrt(self, inter: discord.Interaction, a: int) -> None:
        await inter.response.send_message(f"sqrt({a}) = {a ** 0.5}")

    @app_commands.command(name=_("add"), description=_("Add two numbers"))
    async def add(self, inter: discord.Interaction, a: int, b: int) -> None:
        await inter.response.send_message(f"{a} + {b} = {a + b}")

    @app_commands.command(name=_("subtract"), description=_("Subtract two numbers"))
    async def subtract(self, inter: discord.Interaction, a: int, b: int) -> None:
        await inter.response.send_message(f"{a} - {b} = {a - b}")

    @app_commands.command(name=_("multiply"), description=_("Multiply two numbers"))
    async def multiply(self, inter: discord.Interaction, a: int, b: int) -> None:
        await inter.response.send_message(f"{a} * {b} = {a * b}")

    @app_commands.command(name=_("divide"), description=_("Divide two numbers"))
    async def divide(self, inter: discord.Interaction, a: int, b: int) -> None:
        await inter.response.send_message(f"{a} / {b} = {a / b}")


async def setup(bot: CustomBot) -> None:
    await bot.add_cog(MathGroup(bot))
