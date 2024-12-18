"""Base class for paginators."""

from __future__ import annotations

from io import BufferedIOBase
from os import PathLike
from typing import TYPE_CHECKING, Any, Generic, List, TypeVar, Union

import discord
from discord.ext import commands
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

    async def _send(self, ctx_or_inter: commands.Context | discord.Interaction, *args: Any, **kwargs: Any) -> None:
        if isinstance(ctx_or_inter, commands.Context):
            if self.message is None:
                self.message = await ctx_or_inter.send(*args, **kwargs)
                return
            self.message = await ctx_or_inter.send(*args, **kwargs)
            return
        if self.message is None:
            await ctx_or_inter.response.send_message(*args, **kwargs)
            self.message = await ctx_or_inter.original_response()
            return
        self.message = await ctx_or_inter.edit_original_response(*args, **kwargs)

    async def send_page(self, ctx_or_inter: commands.Context | discord.Interaction, page: T) -> None:
        if isinstance(page, discord.Embed):  # Embed
            # Check if the embed has an associated attachment and send it along with the embed
            attachment = None
            if (page.image.url or "").startswith("attachment://") and len(self.attachments) > self.current_page:
                attachment = discord.File(self.attachments[self.current_page].fp.name)
            attachments = [attachment] if attachment else []
            if self.message is None:
                return await self._send(ctx_or_inter, embed=page, view=self, files=attachments)
            return await self._send(ctx_or_inter, embed=page, view=self, attachments=attachments)

        if isinstance(page, str):  # String
            # Check if the string has an associated attachment and send it along with the string
            attachment = None
            if len(self.attachments) > self.current_page:
                attachment = discord.File(self.attachments[self.current_page].fp.name)
            attachments = [attachment] if attachment else []
            if self.message is None:
                return await self._send(ctx_or_inter, content=page, view=self, files=attachments)
            return await self._send(ctx_or_inter, content=page, view=self, attachments=attachments)

        # File
        file = discord.File(page) if not isinstance(page, discord.File) else discord.File(page.fp.name)
        if self.message is None:
            return await self._send(ctx_or_inter, file=file, view=self)
        return await self._send(ctx_or_inter, file=file, view=self)

    async def start_paginator(
        self, ctx_or_inter: commands.Context | discord.Interaction, *, starting_page: int = 0
    ) -> None:
        self.current_page = starting_page
        page = self.pages[starting_page]
        await self.send_page(ctx_or_inter, page)

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
