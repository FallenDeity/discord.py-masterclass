from __future__ import annotations

import discord

from . import BaseLayoutView

__all__: tuple[str, ...] = ("PokemonGallery",)


class MediaGallery(discord.ui.MediaGallery[discord.ui.LayoutView]):
    def __init__(self, index: int) -> None:
        self.attachments = [discord.File(f"assets/{i}.png") for i in range((index * 3) + 1, (index * 3) + 4)]
        super().__init__(*[discord.MediaGalleryItem(attachment) for attachment in self.attachments])


class StepperRow(discord.ui.ActionRow["PokemonGallery"]):
    view: "PokemonGallery"

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button["PokemonGallery"]):
        self.view._cursor = (self.view._cursor - 1) % self.view._limit
        self.view._update_gallery()
        await self.view._edit(view=self.view, attachments=self.view.media_gallery.attachments)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button["PokemonGallery"]):
        self.view._cursor = (self.view._cursor + 1) % self.view._limit
        self.view._update_gallery()
        await self.view._edit(view=self.view, attachments=self.view.media_gallery.attachments)


class PokemonGallery(BaseLayoutView):
    def __init__(self, user: discord.User | discord.Member, timeout: float = 60):
        super().__init__(user, timeout)
        self._cursor = 0
        self._limit = 3
        self.media_gallery = MediaGallery(index=self._cursor)
        self.add_item(self.media_gallery)
        self.add_item(StepperRow())

    def _update_gallery(self) -> None:
        self.media_gallery.clear_items()
        updated_gallery = MediaGallery(index=self._cursor)
        for item in updated_gallery.attachments:
            self.media_gallery.add_item(media=item)
        self.media_gallery.attachments = updated_gallery.attachments
