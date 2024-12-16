from typing import Any, Iterable, List, Mapping, Optional

import discord
import humanfriendly
from discord.ext import commands
from discord.ext.commands import Cog, Command, Group
from paginators.advanced_paginator import CategoryEntry, EmbedCategoryPaginator
from paginators.button_paginator import EmbedButtonPaginator


class Formatter:
    def __init__(self, help_command: commands.HelpCommand) -> None:
        self.ctx = help_command.context
        self.help_command = help_command

    def __format_command_signature(self, command: commands.Command) -> tuple[str, str]:
        params = self.__format_param(command)
        return f"{command.qualified_name}\n", f"```yaml\n{params}```"

    def __format_param(self, param: commands.Command) -> str:
        signature = self.help_command.get_command_signature(param)
        return signature

    @staticmethod
    def __format_command_help(command: commands.Command) -> str:
        return command.help or "No help provided."

    @staticmethod
    def __format_command_aliases(command: commands.Command) -> str:
        return f"```yaml\nAliases: {', '.join(command.aliases)}```" if command.aliases else "No aliases."

    @staticmethod
    def __format_command_cooldown(command: commands.Command) -> str:
        return (
            f"Cooldown: {humanfriendly.format_timespan(command.cooldown.per, max_units=2)} per user."
            if command.cooldown
            else "No cooldown set."
        )

    @staticmethod
    def __format_command_enabled(command: commands.Command) -> str:
        return f"Enabled: {command.enabled}" if command.enabled else "Command is disabled."

    @staticmethod
    def __format_command_description(command: commands.Command) -> str:
        return command.description or "No description provided."

    def format_command(self, command: commands.Command) -> discord.Embed:
        signature = self.__format_command_signature(command)
        embed = discord.Embed(
            title=signature[0],
            description=signature[1] + self.__format_command_help(command),
            color=discord.Color.blue(),
        )
        embed.add_field(name="Aliases", value=self.__format_command_aliases(command), inline=True)
        embed.add_field(name="Cooldown", value=self.__format_command_cooldown(command), inline=True)
        embed.add_field(name="Enabled", value=self.__format_command_enabled(command), inline=True)
        embed.set_footer(
            text=f"Requested by {self.ctx.author}",
            icon_url=self.ctx.author.display_avatar,
        )
        embed.set_thumbnail(url=self.ctx.bot.user.display_avatar)
        return embed

    async def format_cog_or_group(
        self, cog_or_group: Optional[commands.Cog | commands.Group], commands_: List[commands.Command | commands.Group]
    ) -> List[discord.Embed]:
        category_name = cog_or_group.qualified_name if cog_or_group else "No Category"
        if isinstance(cog_or_group, commands.Group):
            category_desc = cog_or_group.help or "No description provided."
        else:
            category_desc = (
                cog_or_group.description if cog_or_group and cog_or_group.description else "No description provided."
            )
        cog_embed = (
            discord.Embed(
                title=f"{category_name} Commands",
                description=f"*{category_desc}*" or "*No description provided.*",
                color=discord.Color.blue(),
            )
            .set_thumbnail(url=self.ctx.bot.user.display_avatar)
            .set_footer(
                text=f"Requested by {self.ctx.author}",
                icon_url=self.ctx.author.display_avatar,
            )
        )
        embeds: List[discord.Embed] = []
        for i in range(0, len(commands_), 5):
            embed = cog_embed.copy()
            for command in commands_[i : i + 5]:
                signature = self.__format_command_signature(command)
                embed.add_field(
                    name=signature[0],
                    value=signature[1] + self.__format_command_help(command),
                    inline=False,
                )
            embed.set_thumbnail(url=self.ctx.bot.user.display_avatar)
            embeds.append(embed)
        return embeds if embeds else [cog_embed]


class CustomHelpCommand(commands.HelpCommand):
    @staticmethod
    def flatten_commands(commands_: Iterable[commands.Command | commands.Group]) -> List[commands.Command]:
        flattened = []
        for command in commands_:
            if isinstance(command, commands.Group):
                flattened.extend(CustomHelpCommand.flatten_commands(command.commands))
            else:
                flattened.append(command)
        return flattened

    async def send_bot_help(self, mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any]]], /) -> None:
        home_embed = (
            discord.Embed(
                title="Home",
                description="Documentation Bot Home Page - Custom Help Command",
                color=discord.Color.blue(),
            )
            .set_thumbnail(url=self.context.bot.user.display_avatar)
            .set_footer(
                text=f"Requested by {self.context.author}",
                icon_url=self.context.author.display_avatar,
            )
        )

        home_pages: List[discord.Embed] = []

        for i in range(0, len(mapping), 5):
            embed = home_embed.copy()
            for cog, cmds in mapping.items():
                filtered_cmds = await self.filter_commands(self.flatten_commands(cmds), sort=True)
                embed.add_field(
                    name=cog.qualified_name if cog else "No Category",
                    value=f"*{cog.description if cog and cog.description else 'No description provided.'}* `[Commands: {len(filtered_cmds)}]`",
                    inline=False,
                )
            home_pages.append(embed)

        categories: List[CategoryEntry[discord.Embed]] = [
            CategoryEntry(
                category_title="Home",
                category_description="Documentation Bot Home Page",
                pages=home_pages,
            )
        ]
        for cog, cmds in mapping.items():
            filtered_cmds = await self.filter_commands(self.flatten_commands(cmds), sort=True)

            cog_name = cog.qualified_name if cog else "No Category"
            cog_desc = cog.description if cog and cog.description else "No description provided."

            categories.append(
                CategoryEntry(
                    category_title=cog_name,
                    category_description=cog_desc,
                    pages=await Formatter(self).format_cog_or_group(cog, filtered_cmds),
                )
            )

        paginator = EmbedCategoryPaginator(self.context.author, pages=categories)
        await paginator.start_paginator(self.context)

    async def send_cog_help(self, cog: Cog, /) -> None:
        commands_ = await self.filter_commands(self.flatten_commands(cog.get_commands()), sort=True)
        embeds = await Formatter(self).format_cog_or_group(cog, commands_)
        paginator = EmbedButtonPaginator(self.context.author, pages=embeds)
        await paginator.start_paginator(self.context)

    async def send_group_help(self, group: Group[Any, ..., Any], /) -> None:
        commands_ = await self.filter_commands(self.flatten_commands(group.commands), sort=True)
        embeds = await Formatter(self).format_cog_or_group(group, commands_)
        paginator = EmbedButtonPaginator(self.context.author, pages=embeds)
        await paginator.start_paginator(self.context)

    async def send_command_help(self, command: Command[Any, ..., Any], /) -> None:
        command_ = await self.filter_commands([command], sort=True)
        embed = Formatter(self).format_command(command_[0])
        await self.context.send(embed=embed)

    async def send_error_message(self, error: str, /) -> None:
        embed = discord.Embed(
            title="Error",
            description=error,
            color=discord.Color.red(),
        ).set_footer(
            text=f"Requested by {self.context.author}",
            icon_url=self.context.author.display_avatar,
        )
        await self.context.send(embed=embed)
