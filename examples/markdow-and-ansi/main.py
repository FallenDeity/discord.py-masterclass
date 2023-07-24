import enum
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


class Style(enum.IntEnum):
    def __str__(self) -> str:
        return f"{self.value}"


class Colors(Style):
    GRAY = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class BackgroundColors(Style):
    FIREFLY_DARK_BLUE = 40
    ORANGE = 41
    MARBLE_BLUE = 42
    GREYISH_TURQUOISE = 43
    GRAY = 44
    INDIGO = 45
    LIGHT_GRAY = 46
    WHITE = 47


class Styles(Style):
    NORMAL = 0
    BOLD = 1
    UNDERLINE = 4


class AnsiBuilder:
    def __init__(self, text: str = "", *styles: Style) -> None:
        self.styles = styles
        self.cursor = len(text)
        self.text = f"\033[{';'.join(map(str, styles))}m{text}\033[0m" if styles and text else text

    def __add__(self, other: str) -> "AnsiBuilder":
        self.text += other
        self.cursor += len(other)
        return self

    def write(self, cursor: int, text: str) -> "AnsiBuilder":
        if cursor > self.cursor or cursor > len(self.text):
            raise ValueError("Cursor cannot be greater than the length of the text")
        if cursor < 0:
            raise ValueError("Cursor cannot be less than 0")
        self.text = self.text[:cursor] + text + self.text[cursor:]
        self.cursor += len(text)
        return self

    def __str__(self) -> str:
        return self.text

    @classmethod
    def to_ansi(cls, text: str, *styles: Style) -> str:
        return str(cls(text, *styles))

    @property
    def block(self) -> str:
        return f"```ansi\n{self.text}```"


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
load_dotenv()


@bot.command()
async def foreground(ctx: commands.Context[commands.Bot]) -> None:
    fg = AnsiBuilder("Foreground Colors\n", Styles.BOLD)
    for color in Colors:
        fg += AnsiBuilder.to_ansi(f"{color.name}\n", color)
    await ctx.send(fg.block)


@bot.command()
async def background(ctx: commands.Context[commands.Bot]) -> None:
    bg = AnsiBuilder("Background Colors\n", Styles.BOLD)
    for color in BackgroundColors:
        bg += AnsiBuilder.to_ansi(f"{color.name}\n", color)
    await ctx.send(bg.block)


@bot.command()
async def style(ctx: commands.Context[commands.Bot]) -> None:
    _style = AnsiBuilder("Styles\n", Styles.BOLD)
    for s in Styles:
        _style += AnsiBuilder.to_ansi(f"{s.name}\n", s)
    await ctx.send(_style.block)


@bot.command()
async def combo(ctx: commands.Context[commands.Bot]) -> None:
    # combination of all foreground colors on all background colors
    for bg in BackgroundColors:
        combined = AnsiBuilder()
        for fg in Colors:
            combined += f"{AnsiBuilder.to_ansi('Sample', fg, bg)} "
        await ctx.send(combined.block)


@bot.command()
async def style_combo(ctx: commands.Context[commands.Bot], style_: str) -> None:
    if style_ not in Styles.__members__:
        await ctx.send("Invalid style")
        return
    _style = Styles[style_]
    combined = AnsiBuilder()
    for fg in Colors:
        combined += f"{AnsiBuilder.to_ansi('Sample', fg, _style)} "
    await ctx.send(combined.block)


bot.run(str(os.getenv("TOKEN")))
