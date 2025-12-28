from __future__ import annotations

import discord

__all__: tuple[str, ...] = (
    "BasicThumbnailSection",
    "BasicButtonSection",
    "CombinedSectionView",
)


class BasicThumbnailSection(discord.ui.LayoutView):
    section = discord.ui.Section["BasicThumbnailSection"](
        "## Title",
        "Markdown _supported_ text displayed in sections.",
        accessory=discord.ui.Thumbnail["BasicThumbnailSection"]("https://i.imgur.com/9sDnoUW.jpeg"),
    )


class BasicButtonSection(discord.ui.LayoutView):
    section = discord.ui.Section["BasicButtonSection"](
        "## Support",
        "Click the button to contact support.",
        accessory=discord.ui.Button["BasicButtonSection"](
            label="Contact Support", style=discord.ButtonStyle.link, url="https://support.example.com"
        ),
    )


class CombinedSectionView(discord.ui.LayoutView):
    thumbnail_section = discord.ui.Section["CombinedSectionView"](
        "## Avatar",
        "This section displays a thumbnail accessory.",
        accessory=discord.ui.Thumbnail["CombinedSectionView"]("https://i.imgur.com/9sDnoUW.jpeg"),
    )
    button_section = discord.ui.Section["CombinedSectionView"](
        "## Support",
        "Click the button to contact support.",
        accessory=discord.ui.Button["CombinedSectionView"](
            label="Contact Support", style=discord.ButtonStyle.link, url="https://support.example.com"
        ),
    )
