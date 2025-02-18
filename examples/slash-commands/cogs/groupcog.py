from __future__ import annotations

import typing

import discord
from discord import app_commands
from discord.ext import commands

if typing.TYPE_CHECKING:
    from .. import CustomBot


class MathGroup(commands.GroupCog, name="math", description="Math commands"):
    group = app_commands.Group(name="functions", description="Math functions")

    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot
        super().__init__()

    @group.command(name="pow", description="Raise a number to a power")
    async def power(self, inter: discord.Interaction, a: int, b: int) -> None:
        """
        Raise a number to a power.

        Parameters
        ----------
        inter : discord.Interaction
            The interaction.
        a : int
            The number.
        b : int
            The power.
        """
        await inter.response.send_message(f"{a} ^ {b} = {a ** b}")

    @app_commands.command(name="add", description="Add two numbers")
    async def add(self, inter: discord.Interaction, a: int, b: int) -> None:
        """
        Add two numbers.

        Parameters
        ----------
        inter : discord.Interaction
            The interaction.
        a : int
            The first number.
        b : int
            The second number.
        """
        await inter.response.send_message(f"{a} + {b} = {a + b}")

    @app_commands.command(name="subtract", description="Subtract two numbers")
    async def subtract(self, inter: discord.Interaction, a: int, b: int) -> None:
        """
        Subtract two numbers.

        Parameters
        ----------
        inter : discord.Interaction
            The interaction.
        a : int
            The first number.
        b : int
            The second number.
        """
        await inter.response.send_message(f"{a} - {b} = {a - b}")

    @commands.hybrid_command(name="multiply", description="Multiply two numbers")
    async def multiply(self, ctx: commands.Context[CustomBot], a: int, b: int) -> None:
        """
        Multiply two numbers.

        Parameters
        ----------
        ctx : commands.Context
            The context.
        a : int
            The first number.
        b : int
            The second number.
        """
        await ctx.send(f"{a} * {b} = {a * b}")

    @commands.command(name="divide", description="Divide two numbers")
    async def divide(self, ctx: commands.Context[CustomBot], a: int, b: int) -> None:
        """
        Divide two numbers.

        Parameters
        ----------
        ctx : commands.Context
            The context.
        a : int
            The first number.
        b : int
            The second number.
        """
        await ctx.send(f"{a} / {b} = {a / b}")


async def setup(bot: CustomBot) -> None:
    await bot.add_cog(MathGroup(bot))
