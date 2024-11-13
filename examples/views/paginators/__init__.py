"""Base class for paginators."""

from __future__ import annotations

import asyncio
from io import BufferedIOBase
from os import PathLike
from typing import TYPE_CHECKING, Any, Generic, List, TypeVar, Union

import discord
from views import BaseView

# we use the BaseView class defined in the other example

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

PageLike: TypeAlias = Union[discord.Embed, str, bytes, PathLike[Any], BufferedIOBase]
FileLike: TypeAlias = Union[str, bytes, PathLike[Any], BufferedIOBase]

T = TypeVar("T", bound=PageLike)


class BasePaginator(Generic[T], BaseView):
    pages: List[T]
    current_page: int

    def __init__(self, user: Union[discord.User, discord.Member], pages: List[T]) -> None:
        super().__init__(user=user, timeout=180)
        self.pages = pages
        self.current_page: int = 0

    async def send_page(self, inter: discord.Interaction, page: T) -> None:
        if isinstance(page, discord.Embed):
            if self.message is None:
                return await inter.response.send_message(embed=page, view=self)
            await inter.edit_original_response(embed=page, view=self)
            return

        if self.message is None:
            return await inter.response.send_message(file=discord.File(page), view=self)
        await inter.edit_original_response(attachments=[discord.File(page)], view=self)

    async def start_paginator(self, inter: discord.Interaction, *, starting_page: int = 0) -> None:
        self.current_page = starting_page
        page = self.pages[starting_page]
        await self.send_page(inter, page)
        await asyncio.sleep(1)
        self.message = await inter.original_response()

    async def stop_paginator(self) -> None:
        self._disable_all()
        await self._edit(view=self)

    async def next_page(self, inter: discord.Interaction) -> None:
        self.current_page = (self.current_page + 1) % len(self.pages)
        page = self.pages[self.current_page]
        await self.send_page(inter, page)

    async def previous_page(self, inter: discord.Interaction) -> None:
        self.current_page = (self.current_page - 1) % len(self.pages)
        page = self.pages[self.current_page]
        await self.send_page(inter, page)
