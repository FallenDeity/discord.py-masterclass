from __future__ import annotations

from typing import Optional, Generic, List, TypeVar, Union

import discord
from discord import File, Member, User

from paginators import PageLike, FileLike
from paginators.button_paginator import ButtonBasedPaginator


T = TypeVar("T", bound=PageLike)


class CategoryEntry(Generic[T]):
    def __init__(
        self,
        value: T,
        *,
        category_title: str,
        category_description: Optional[str] = None,
        pages: Optional[List[T]] = None,
    ) -> None:
        self.category_title = category_title
        self.category_description = category_description
        self.value = value
        self.pages = pages or []
    
    def add_page(self, page: T) -> None:
        self.pages.append(page)


class CategoryBasedPaginator(Generic[T], ButtonBasedPaginator[T]):
    def __init__(
        self,
        user: Union[User, Member],
        *,
        pages: List[CategoryEntry[T]],
    ) -> None:
        self.categories = pages
        self.current_category: int = 0
        self.current_page: int = 0

        self.select = CategoryPaginatorSelect()
        for i, page in enumerate(pages):
            self.select.add_option(
                label=page.category_title,
                value=str(i),
                description=page.category_description,
            )
        self.add_item(self.select)


class CategoryPaginatorSelect(discord.ui.Select[CategoryBasedPaginator[PageLike]]):
    def __init__(self) -> None:
        super().__init__(min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        # the user can only select one value and shoud at least select it
        # so this is always fine
        await interaction.response.defer()
        self.base_view.current_page = int(self.values[0])
        page = self.base_view.pages[self.base_view.current_page]
        await self.base_view.send_page(interaction, page)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await self.base_view.interaction_check(interaction)
