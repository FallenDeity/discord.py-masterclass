"""Base class for paginators."""

from __future__ import annotations

from io import BufferedIOBase
from os import PathLike
from typing import TYPE_CHECKING, Any, Generic, List, TypeVar, Union

import discord
from views import BaseView

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

PageLike: TypeAlias = Union[discord.Embed, str, bytes, PathLike[Any], BufferedIOBase, discord.File]
FileLike: TypeAlias = Union[str, bytes, PathLike[Any], BufferedIOBase]

T = TypeVar("T", bound=PageLike)


class BasePaginator(Generic[T], BaseView):
    pages: List[T]
    current_page: int

    def __init__(
        self, user: Union[discord.User, discord.Member], pages: List[T], *, attachments: List[discord.File] = None
    ) -> None:
        super().__init__(user=user, timeout=180)
        self.pages = pages
        self.current_page: int = 0
        self.attachments = attachments or []

    async def send_page(self, inter: discord.Interaction, page: T) -> None:
        if isinstance(page, discord.Embed):  # Embed
            # Check if the embed has an associated attachment and send it along with the embed
            attachment = None
            if (page.image.url or "").startswith("attachment://") and len(self.attachments) > self.current_page:
                attachment = discord.File(self.attachments[self.current_page].fp.name)
            attachments = [attachment] if attachment else []
            if self.message is None:
                return await inter.response.send_message(embed=page, view=self, files=attachments)
            self.message = await inter.edit_original_response(embed=page, view=self, attachments=attachments)
            return

        if isinstance(page, str):  # String
            # Check if the string has an associated attachment and send it along with the string
            attachment = None
            if len(self.attachments) > self.current_page:
                attachment = discord.File(self.attachments[self.current_page].fp.name)
            attachments = [attachment] if attachment else []
            if self.message is None:
                return await inter.response.send_message(content=page, view=self, files=attachments)
            self.message = await inter.edit_original_response(content=page, view=self, attachments=attachments)
            return

        # File
        file = discord.File(page) if not isinstance(page, discord.File) else discord.File(page.fp.name)
        if self.message is None:
            return await inter.response.send_message(file=file, view=self)
        self.message = await inter.edit_original_response(attachments=[file], view=self)

    async def start_paginator(self, inter: discord.Interaction, *, starting_page: int = 0) -> None:
        self.current_page = starting_page
        page = self.pages[starting_page]
        await self.send_page(inter, page)
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
