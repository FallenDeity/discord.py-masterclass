from __future__ import annotations

from typing import TYPE_CHECKING, Generic, List, TypeVar, Union

import discord
from discord import PartialEmoji
from paginators import BasePaginator, FileLike, PageLike

if TYPE_CHECKING:
    from views import BaseView


T = TypeVar("T", bound=PageLike)


class ButtonBasedPaginator(Generic[T], BasePaginator[T]):
    @discord.ui.button(emoji=PartialEmoji.from_str("⏪"))
    async def goto_first_page_callback(self, inter: discord.Interaction, _: discord.ui.Button[BaseView]) -> None:
        await inter.response.defer()
        self.current_page = 0
        page = self.pages[self.current_page]
        await self.send_page(inter, page)

    @discord.ui.button(emoji=PartialEmoji.from_str("◀️"))
    async def previous_page_callback(self, inter: discord.Interaction, _: discord.ui.Button[BaseView]) -> None:
        await inter.response.defer()
        await self.previous_page(inter)

    @discord.ui.button(emoji=PartialEmoji.from_str("▶️"))
    async def next_page_callback(self, inter: discord.Interaction, _: discord.ui.Button[BaseView]) -> None:
        await inter.response.defer()
        await self.next_page(inter)

    @discord.ui.button(emoji=PartialEmoji.from_str("⏩"))
    async def goto_last_page_callback(self, inter: discord.Interaction, _: discord.ui.Button[BaseView]) -> None:
        await inter.response.defer()
        self.current_page = len(self.pages) - 1
        page = self.pages[self.current_page]
        await self.send_page(inter, page)

    @discord.ui.button(emoji=PartialEmoji.from_str("🗑️"))
    async def stop_paginator_callback(self, inter: discord.Interaction, _: discord.ui.Button[BaseView]) -> None:
        await inter.response.defer()
        await self.stop_paginator()


class EmbedButtonPaginator(ButtonBasedPaginator[discord.Embed]):
    def __init__(
        self,
        user: Union[discord.User, discord.Member],
        pages: List[discord.Embed],
        *,
        attachments: List[discord.File] = None,
    ) -> None:
        super().__init__(user, pages, attachments=attachments)


class FileButtonPaginator(ButtonBasedPaginator[FileLike]):
    def __init__(self, user: Union[discord.User, discord.Member], pages: List[FileLike]) -> None:
        super().__init__(user, pages)
