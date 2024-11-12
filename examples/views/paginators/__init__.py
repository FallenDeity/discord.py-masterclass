"""Base class for paginators."""
from __future__ import annotations
from typing import TypeVar, Union, Generic, List, Any, TYPE_CHECKING

import asyncio
from os import PathLike
from io import BufferedIOBase

import discord

# we use the BaseView class defined in the other example
from views import BaseView

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
        # if we are at the end of the pages list
        # we start again from the first page
        # otherwise we normally increment the page index
        if self.current_page == (len(self.pages) - 1):
            self.current_page = 0
        else:
            self.current_page += 1
        page = self.pages[self.current_page]
        await self.send_page(inter, page)
    
    async def previous_page(self, inter: discord.Interaction) -> None:
        # if we are at the start of the pages list
        # we start again from the last page
        # otherwise we normally decrement the page index
        if self.current_page == 0:
            self.current_page = len(self.pages) - 1
        else:
            self.current_page -= 1
        page = self.pages[self.current_page]
        await self.send_page(inter, page)
