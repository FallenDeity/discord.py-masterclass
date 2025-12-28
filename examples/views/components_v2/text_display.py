from __future__ import annotations

import discord
from views import BaseModal

__all__: tuple[str, ...] = (
    "SimpleTextDisplayView",
    "ModalTextDisplayView",
    "MultipleTextDisplayView",
)


class MarkdownShowcase(discord.ui.TextDisplay[discord.ui.LayoutView]):
    def __init__(self) -> None:
        super().__init__(
            content=(
                "# Header 1\n"
                "## Header 2\n"
                "### Header 3\n\n"
                "**Bold Text**\n"
                "*Italic Text*\n"
                "***Bold Italic Text***\n\n"
                "> :sparkles: This is a blockquote.\n\n"
                "- Item 1\n"
                "- Item 2\n"
                "- Item 3\n\n"
                "`Inline code` example.\n\n"
                "```python\n"
                "def hello_world():\n"
                "    print('Hello, world!')\n"
                "```\n\n"
                "[Discord.py](https://discordpy.dev) link example."
            )
        )


class SimpleTextDisplayView(discord.ui.LayoutView):
    text_display = MarkdownShowcase()


class ModalTextDisplayView(BaseModal, title="Modal with Text Display"):
    text_display = MarkdownShowcase()


class MultipleTextDisplayView(discord.ui.LayoutView):
    header = discord.ui.TextDisplay["SimpleTextDisplayView"](
        content="# Welcome to the Bot\n" "This is a simple text display example."
    )
    separator = discord.ui.Separator["SimpleTextDisplayView"]()
    instructions = discord.ui.TextDisplay["SimpleTextDisplayView"](
        content="## Instructions\n"
        "1. Use `/help` to get a list of commands.\n"
        "2. Use `/info` to get information about the bot."
    )
