import discord
from discord import app_commands
from discord.ext import commands


class SuperCog(commands.GroupCog, name="foo", description="A super cog"):
    _bar = app_commands.Group(name="bar", description="A bar group")

    @app_commands.command()
    async def foo(self, inter: discord.Interaction):
        await inter.response.send_message("foo")

    @_bar.command()
    async def baz(self, inter: discord.Interaction):
        await inter.response.send_message("baz")


async def setup(bot: commands.Bot):
    await bot.add_cog(SuperCog())
