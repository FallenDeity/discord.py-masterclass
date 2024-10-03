from discord.ext import commands


class SubCog(commands.Cog): ...


async def setup(bot: commands.Bot):
    await bot.add_cog(SubCog())
