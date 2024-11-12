from __future__ import annotations

import datetime
import logging
import os
import re
import traceback
import typing

import aiohttp
import discord
from discord.ext import commands
from discord.ui.item import Item
from dotenv import load_dotenv
from views import BaseModal, BaseView
from paginators.button_paginator import EmbedButtonPaginator, FileButtonPaginator
from paginators.select_paginator import EmbedSelectPaginator, FileSelectPaginator


class TagModal(BaseModal, title="Tag Creation"):
    tag_title = discord.ui.TextInput[BaseModal](
        label="Tag Title", placeholder="Enter a tag title", min_length=1, max_length=100, style=discord.TextStyle.short
    )
    tag_content = discord.ui.TextInput[BaseModal](
        label="Tag Content",
        placeholder="Enter a tag content",
        min_length=1,
        max_length=300,
        style=discord.TextStyle.long,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title=self.tag_title.value, description=self.tag_content.value, color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar)
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await super().on_submit(interaction)


class Menus(BaseView):
    @discord.ui.select(
        cls=discord.ui.Select,
        options=[discord.SelectOption(emoji=f"{chr(127462 + i)}", label=f"{chr(65 + i)}") for i in range(26)][:25],
        placeholder="Select a letter",
        min_values=1,
        max_values=1,
    )
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select[Menus]) -> None:
        await interaction.response.defer()
        await interaction.followup.send(f"You selected {select.values[0]}", ephemeral=True)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Select a channel",
        min_values=1,
        max_values=1,
    )
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect[Menus]) -> None:
        await interaction.response.defer()
        await interaction.followup.send(f"You selected {select.values[0]}", ephemeral=True)

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Select a role",
        min_values=1,
        max_values=1,
    )
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.RoleSelect[Menus]) -> None:
        await interaction.response.defer()
        await interaction.followup.send(f"You selected {select.values[0]}", ephemeral=True)

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="Select a user",
        min_values=1,
        max_values=1,
    )
    async def user_select(self, interaction: discord.Interaction, select: discord.ui.UserSelect[Menus]) -> None:
        await interaction.response.defer()
        await interaction.followup.send(f"You selected {select.values[0]}", ephemeral=True)

    @discord.ui.select(
        cls=discord.ui.MentionableSelect,
        placeholder="Select a mentionable",
        min_values=1,
        max_values=1,
    )
    async def mentionable_select(
        self, interaction: discord.Interaction, select: discord.ui.MentionableSelect[Menus]
    ) -> None:
        await interaction.response.defer()
        await interaction.followup.send(f"You selected {select.values[0]}", ephemeral=True)


class ConfirmView(BaseView):
    confirmed: bool = False

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.gray, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button[BaseView]) -> None:
        await interaction.response.defer()
        self.confirmed = True
        self._disable_all()
        await self._edit(content="Confirmed", view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button[BaseView]) -> None:
        await interaction.response.defer()
        self._disable_all()
        await self._edit(content="Cancelled", view=self)
        self.stop()


class PersistentMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.menu = discord.ui.Select[PersistentMenu](
            custom_id="persistent_menu",
            placeholder="Select a letter",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(emoji=f"{chr(127462 + i)}", label=f"{chr(65 + i)}") for i in range(26)][:25],
        )
        self.menu.callback = self.callback
        self.add_item(self.menu)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        assert interaction.data is not None and "custom_id" in interaction.data, "Invalid interaction data"
        await interaction.followup.send(f"You clicked {self.menu.values[0]}", ephemeral=True)


class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        colors = [
            discord.ButtonStyle.red,
            discord.ButtonStyle.blurple,
            discord.ButtonStyle.green,
            discord.ButtonStyle.grey,
        ]
        for color in colors:
            self.add_item(discord.ui.Button(label=color.name.title(), style=color, custom_id=color.name))
            self.children[-1].callback = self.callback

    async def callback(self, interaction: discord.Interaction) -> None:
        assert interaction.data is not None and "custom_id" in interaction.data, "Invalid interaction data"
        await interaction.response.send_message(f"You clicked {interaction.data['custom_id']}", ephemeral=True)


class DynamicSelect(
    discord.ui.DynamicItem[discord.ui.Select[discord.ui.View]], template=r"select-user:(?P<user_id>\d+)"
):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(
            discord.ui.Select(
                custom_id=f"select-user:{user_id}",
                placeholder="Select a letter",
                min_values=1,
                max_values=1,
                options=[discord.SelectOption(emoji=f"{chr(127462 + i)}", label=f"{chr(65 + i)}") for i in range(26)][
                    :25
                ],
            )
        )

    # This method needs to be implemented when subclassing DynamicItem
    @classmethod
    async def from_custom_id(
        cls, interaction: discord.Interaction, item: Item[typing.Any], match: re.Match[str]
    ) -> discord.ui.DynamicItem[typing.Any]:
        return cls(int(match.group("user_id")))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        assert interaction.data is not None and "custom_id" in interaction.data, "Invalid interaction data"
        await interaction.followup.send(f"You clicked {self.item.values[0]}", ephemeral=True)


class DynamicCounter(
    discord.ui.DynamicItem[discord.ui.Button[discord.ui.View]], template=r"counter:(?P<count>\d+):user:(?P<user_id>\d+)"
):
    def __init__(self, count: int, user_id: int):
        self.count = count
        self.user_id = user_id
        super().__init__(
            discord.ui.Button(
                style=discord.ButtonStyle.blurple, label=str(count), custom_id=f"counter:{count}:user:{user_id}"
            )
        )

    # This method needs to be implemented when subclassing DynamicItem
    @classmethod
    async def from_custom_id(
        cls, interaction: discord.Interaction, item: Item[typing.Any], match: re.Match[str]
    ) -> discord.ui.DynamicItem[typing.Any]:
        return cls(int(match.group("count")), int(match.group("user_id")))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def callback(self, interaction: discord.Interaction) -> None:
        self.count += 1
        self.item.label = str(self.count)
        self.item.custom_id = f"counter:{self.count}:user:{self.user_id}"
        await interaction.response.edit_message(view=self.view)


class CustomBot(commands.Bot):
    client: aiohttp.ClientSession
    _uptime: datetime.datetime

    def __init__(self, prefix: str, ext_dir: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(*args, **kwargs, command_prefix=commands.when_mentioned_or(prefix), intents=intents)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ext_dir = ext_dir
        self.synced = False

    async def _load_extensions(self) -> None:
        if not os.path.isdir(self.ext_dir):
            self.logger.error(f"Extension directory {self.ext_dir} does not exist.")
            return
        for filename in os.listdir(self.ext_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"{self.ext_dir}.{filename[:-3]}")
                    self.logger.info(f"Loaded extension {filename[:-3]}")
                except commands.ExtensionError:
                    self.logger.error(f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}")

    async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.logger.error(f"An error occurred in {event_method}.\n{traceback.format_exc()}")

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    async def setup_hook(self) -> None:
        self.add_dynamic_items(DynamicSelect)
        self.add_dynamic_items(DynamicCounter)
        self.add_view(PersistentMenu())
        self.add_view(PersistentView())
        self.client = aiohttp.ClientSession()
        await self._load_extensions()
        if not self.synced:
            await self.tree.sync()
            self.synced = not self.synced
            self.logger.info("Synced command tree")

    async def close(self) -> None:
        await super().close()
        await self.client.close()

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        load_dotenv()
        try:
            super().run(str(os.getenv("TOKEN")), *args, **kwargs)
        except (discord.LoginFailure, KeyboardInterrupt):
            self.logger.info("Exiting...")
            exit()

    @property
    def user(self) -> discord.ClientUser:
        assert super().user, "Bot is not ready yet"
        return typing.cast(discord.ClientUser, super().user)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.utcnow() - self._uptime


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
    bot = CustomBot(prefix="!", ext_dir="cogs")

    @bot.command()
    async def persistent(ctx: commands.Context[CustomBot]):
        """A command to test persistent views"""
        await ctx.send("Persistent View", view=PersistentView())

    @bot.command()
    async def persistent_counter(ctx: commands.Context[CustomBot]):
        """A command to test persistent counters"""
        view = discord.ui.View(timeout=None)
        view.add_item(DynamicCounter(0, ctx.author.id))
        await ctx.send("Persistent Counter", view=view)

    @bot.command()
    async def confirm(ctx: commands.Context[CustomBot], user: discord.Member):
        """A command to test confirm views"""
        view = ConfirmView(user=user)
        await ctx.send(f"Confirm {user.mention}?", view=view)
        await view.wait()
        await ctx.send(f"Confirmed: {view.confirmed}")

    @bot.command()
    async def select(ctx: commands.Context[CustomBot]):
        """A command to test select menus"""
        view = Menus(user=ctx.author)
        view.message = await ctx.send("Check out these menus!", view=view)

    @bot.command()
    async def persistent_menu(ctx: commands.Context[CustomBot]):
        """A command to test persistent menus"""
        await ctx.send("Persistent Menu", view=PersistentMenu())

    @bot.command()
    async def dynamic_select(ctx: commands.Context[CustomBot]):
        """A command to test dynamic select menus"""
        view = discord.ui.View(timeout=None)
        view.add_item(DynamicSelect(ctx.author.id))
        await ctx.send("Dynamic Select", view=view)

    @bot.tree.command()
    async def modal(inter: discord.Interaction):
        """A command to test modals"""
        await inter.response.send_modal(TagModal(timeout=60.0))

    @bot.tree.command()
    async def embed_button_paginators(inter: discord.Interaction):
        embeds = [
            discord.Embed(title="sus"),
            discord.Embed(title="lmao"),
            discord.Embed(title="sus1"),
            discord.Embed(title="lmao2"),
        ]
        paginator = EmbedButtonPaginator(inter.user, embeds)
        await paginator.start_paginator(inter)

    @bot.tree.command()
    async def file_button_paginators(interaction: discord.Interaction):
        files = [
            "cc.png",
            "cc.png",
            "cc.png"
        ]
        paginator = FileButtonPaginator(interaction.user, files)
        await paginator.start_paginator(interaction)

    bot.run()


if __name__ == "__main__":
    main()
