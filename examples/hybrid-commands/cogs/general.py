from __future__ import annotations

import typing

from discord.ext import commands

if typing.TYPE_CHECKING:
    from .. import CustomBot


class General(commands.Cog):
    """General commands"""

    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping")
    async def ping(self, ctx: commands.Context[CustomBot]) -> None:
        """Pong!"""
        await ctx.defer(ephemeral=True)
        await ctx.send(f"Pong! ({self.bot.latency * 1000:.2f}ms)")

    @commands.hybrid_group(name="math")
    async def math(self, ctx: commands.Context[CustomBot]) -> None:
        """Math commands"""
        pass

    @math.command(name="add")
    async def add(self, ctx: commands.Context[CustomBot], a: int, b: int) -> None:
        """Add two numbers"""
        await ctx.send(f"{a} + {b} = {a + b}")

    @math.command(name="subtract")
    async def subtract(self, ctx: commands.Context[CustomBot], a: int, b: int) -> None:
        """Subtract two numbers"""
        await ctx.send(f"{a} - {b} = {a - b}")


async def setup(bot: CustomBot) -> None:
    await bot.add_cog(General(bot))
