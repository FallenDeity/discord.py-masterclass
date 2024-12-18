from __future__ import annotations

from typing import Generic, List, Optional, TypeVar, Union

import discord
from paginators import BasePaginator, FileLike, PageLike

T = TypeVar("T", bound=PageLike)


class PageEntry(Generic[T]):
    def __init__(
        self,
        value: T,
        *,
        page_title: str,
        page_description: Optional[str] = None,
        attachment: discord.File = None,
    ) -> None:
        self.page_title = page_title
        self.page_description = page_description
        self.value = value
        self.attachment = attachment


class SelectMenuBasedPaginator(Generic[T], BasePaginator[T]):
    def __init__(
        self,
        user: Union[discord.User, discord.Member],
        *,
        pages: List[PageEntry[T]],
    ) -> None:
        self.select = PaginatorSelect(view=self)
        pages_: List[T] = []
        attachments_: List[discord.File] = []
        for i, page in enumerate(pages):
            pages_.append(page.value)
            if page.attachment:
                attachments_.append(page.attachment)
            self.select.add_option(
                label=page.page_title,
                value=str(i),
                description=page.page_description,
            )
        super().__init__(user, pages=pages_, attachments=attachments_)
        self.add_item(self.select)


class PaginatorSelect(discord.ui.Select[SelectMenuBasedPaginator[PageLike]]):
    def __init__(self, view: SelectMenuBasedPaginator[PageLike]) -> None:
        super().__init__(min_values=1, max_values=1)
        self.base_view = view

    async def callback(self, interaction: discord.Interaction) -> None:
        # the user can only select one value and shoud at least select it
        # so this is always fine
        await interaction.response.defer()
        self.base_view.current_page = int(self.values[0])
        page = self.base_view.pages[self.base_view.current_page]
        await self.base_view.send_page(interaction, page)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await self.base_view.interaction_check(interaction)


class EmbedSelectPaginator(SelectMenuBasedPaginator[discord.Embed]):
    def __init__(self, user: Union[discord.User, discord.Member], *, pages: List[PageEntry[discord.Embed]]) -> None:
        super().__init__(user, pages=pages)


class FileSelectPaginator(SelectMenuBasedPaginator[FileLike]):
    def __init__(self, user: Union[discord.User, discord.Member], *, pages: List[PageEntry[FileLike]]) -> None:
        super().__init__(user, pages=pages)


class StringSelectPaginator(SelectMenuBasedPaginator[str]):
    def __init__(self, user: Union[discord.User, discord.Member], *, pages: List[PageEntry[str]]) -> None:
        super().__init__(user, pages=pages)
