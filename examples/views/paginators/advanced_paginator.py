from __future__ import annotations

from typing import Generic, List, Optional, TypeVar, Union

import discord
from discord import File, Member, User
from paginators import FileLike, PageLike
from paginators.button_paginator import ButtonBasedPaginator

T = TypeVar("T", bound=PageLike)


class CategoryEntry(Generic[T]):
    def __init__(
        self,
        *,
        category_title: str,
        category_description: Optional[str] = None,
        pages: Optional[List[T]] = None,
        attachments: Optional[List[File]] = None,
    ) -> None:
        self.category_title = category_title
        self.category_description = category_description
        self.pages = pages or []
        self.attachments = attachments or []

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

        super().__init__(user, pages[self.current_category].pages, attachments=pages[self.current_category].attachments)

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
        self.view.current_category = int(self.values[0])
        view: CategoryBasedPaginator[PageLike] = self.view
        view.pages = view.categories[self.view.current_category].pages
        view.attachments = view.categories[self.view.current_category].attachments
        view.current_page = 0
        page = view.pages[view.current_page]
        await view.send_page(interaction, page)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await self.view.interaction_check(interaction)


class EmbedCategoryPaginator(CategoryBasedPaginator[discord.Embed]):
    def __init__(self, user: Union[discord.User, discord.Member], *, pages: List[CategoryEntry[discord.Embed]]) -> None:
        super().__init__(user, pages=pages)


class FileCategoryPaginator(CategoryBasedPaginator[FileLike]):
    def __init__(self, user: Union[discord.User, discord.Member], *, pages: List[CategoryEntry[FileLike]]) -> None:
        super().__init__(user, pages=pages)


class StringCategoryPaginator(CategoryBasedPaginator[str]):
    def __init__(self, user: Union[discord.User, discord.Member], *, pages: List[CategoryEntry[str]]) -> None:
        super().__init__(user, pages=pages)
