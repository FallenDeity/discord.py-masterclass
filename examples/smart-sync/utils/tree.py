from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Sequence

import attrs
import discord
from discord import app_commands
from discord.abc import Snowflake
from discord.app_commands.errors import AppCommandError
from discord.app_commands.models import AppCommand
from discord.http import Route
from discord.interactions import Interaction
from tabulate import tabulate

if TYPE_CHECKING:
    from .. import CustomBot  # noqa: F401


@attrs.define(kw_only=True)
class Diff:
    same: list[AppCommandDict]
    added: list[AppCommandDict]
    removed: list[AppCommandDict]
    updated: list[AppCommandDict]

    def __str__(self) -> str:
        table = tabulate(
            [[cmd.name, cmd.type, "Added"] for cmd in self.added]
            + [[cmd.name, cmd.type, "Removed"] for cmd in self.removed]
            + [[cmd.name, cmd.type, "Updated"] for cmd in self.updated],
            headers=["Name", "Type", "Change"],
        )
        return table


@attrs.define(kw_only=True, frozen=True)
class AppCommandGroupOption:
    name: str
    description: str
    type: discord.AppCommandOptionType
    options: list[AppCommandOption | AppCommandGroupOption]
    name_localizations: dict[discord.Locale, str]
    description_localizations: dict[discord.Locale, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "options": [opt.to_dict() for opt in self.options],
            "name_localizations": {k.name: v for k, v in self.name_localizations.items()},
            "description_localizations": {k.name: v for k, v in self.description_localizations.items()},
        }

    @classmethod
    def from_app_command_group(cls, cmd: app_commands.AppCommandGroup) -> AppCommandGroupOption:
        return cls(
            name=cmd.name,
            description=cmd.description,
            type=cmd.type,
            options=[AppCommandOption.from_option(opt) for opt in cmd.options],
            name_localizations=cmd.name_localizations,
            description_localizations=cmd.description_localizations,
        )

    @classmethod
    def from_command(cls, data: dict[str, Any], cmd: app_commands.Command | app_commands.Group) -> AppCommandGroupOption:  # type: ignore
        if isinstance(cmd, app_commands.Command):
            return cls(
                name=cmd.name,
                description=cmd.description,
                type=discord.AppCommandOptionType(cmd.to_dict()["type"]),
                options=[
                    AppCommandOption.from_parameter(d, param) for d, param in zip(data["options"], cmd.parameters)
                ],
                name_localizations={discord.Locale(k): v for k, v in data.get("name_localizations", {}).items()},
                description_localizations={
                    discord.Locale(k): v for k, v in data.get("description_localizations", {}).items()
                },
            )
        return cls(
            name=cmd.name,
            description=cmd.description,
            type=discord.AppCommandOptionType(cmd.to_dict()["type"]),
            options=[AppCommandGroupOption.from_command(data["options"][n], opt) for n, opt in enumerate(cmd.commands)],
            name_localizations={discord.Locale(k): v for k, v in data.get("name_localizations", {}).items()},
            description_localizations={
                discord.Locale(k): v for k, v in data.get("description_localizations", {}).items()
            },
        )


@attrs.define(kw_only=True, frozen=True)
class AppCommandOption:
    name: str
    description: str
    required: bool
    type: discord.AppCommandOptionType
    autocomplete: bool
    min_value: int | float | None
    max_value: int | float | None
    min_length: int | None
    max_length: int | None
    channel_types: list[discord.ChannelType]
    choices: list[app_commands.Choice[str | int | float]]
    name_localizations: dict[discord.Locale, str]
    description_localizations: dict[discord.Locale, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required,
            "type": self.type.value,
            "autocomplete": self.autocomplete,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "channel_types": [ct.value for ct in self.channel_types],
            "choices": [{"name": choice.name, "value": choice.value} for choice in self.choices],
            "name_localizations": {k.name: v for k, v in self.name_localizations.items()},
            "description_localizations": {k.name: v for k, v in self.description_localizations.items()},
        }

    @classmethod
    def from_option(
        cls, opt: app_commands.Argument | app_commands.AppCommandGroup
    ) -> AppCommandOption | AppCommandGroupOption:
        if isinstance(opt, app_commands.Argument):
            return cls(
                name=opt.name,
                description=opt.description,
                required=opt.required,
                type=opt.type,
                autocomplete=opt.autocomplete,
                min_value=opt.min_value,
                max_value=opt.max_value,
                min_length=opt.min_length,
                max_length=opt.max_length,
                channel_types=opt.channel_types,
                choices=opt.choices,
                name_localizations=opt.name_localizations,
                description_localizations=opt.description_localizations,
            )
        return AppCommandGroupOption.from_app_command_group(opt)

    @classmethod
    def from_parameter(cls, data: dict[str, Any], param: app_commands.Parameter) -> AppCommandOption:
        return cls(
            name=param.name,
            description=param.description,
            required=param.required,
            type=param.type,
            autocomplete=param.autocomplete,
            min_value=param.min_value,
            max_value=param.max_value,
            min_length=int(param.min_value) if param.min_value else None,
            max_length=int(param.max_value) if param.max_value else None,
            channel_types=param.channel_types,
            choices=param.choices,
            name_localizations={discord.Locale(k): v for k, v in data.get("name_localizations", {}).items()},
            description_localizations={
                discord.Locale(k): v for k, v in data.get("description_localizations", {}).items()
            },
        )


@attrs.define(kw_only=True, frozen=True)
class AppCommandDict:
    type: discord.AppCommandType
    name: str
    description: str
    default_member_permissions: discord.Permissions | None
    dm_permission: bool
    nsfw: bool
    options: list[AppCommandOption | AppCommandGroupOption]
    description_localizations: dict[discord.Locale, str]
    name_localizations: dict[discord.Locale, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "default_member_permissions": getattr(self.default_member_permissions, "value", None),
            "dm_permission": self.dm_permission,
            "nsfw": self.nsfw,
            "options": [opt.to_dict() for opt in self.options],
            "description_localizations": {k.name: v for k, v in self.description_localizations.items()},
            "name_localizations": {k.name: v for k, v in self.name_localizations.items()},
        }

    @classmethod
    def from_app_command(cls, cmd: AppCommand) -> AppCommandDict:
        return cls(
            type=cmd.type,
            name=cmd.name,
            description=cmd.description,
            default_member_permissions=cmd.default_member_permissions,
            dm_permission=cmd.dm_permission,
            nsfw=cmd.nsfw,
            options=[AppCommandOption.from_option(opt) for opt in cmd.options],
            description_localizations=cmd.description_localizations,
            name_localizations=cmd.name_localizations,
        )

    @classmethod
    def from_command(cls, data: dict[str, Any], cmd: app_commands.Command | app_commands.ContextMenu | app_commands.Group):  # type: ignore
        common_data = data.copy()
        common_data["name_localizations"] = common_data.get("name_localizations", {})
        common_data["description_localizations"] = common_data.get("description_localizations", {})
        common_data["type"] = discord.AppCommandType(common_data["type"])
        common_data["default_member_permissions"] = (
            discord.Permissions(common_data["default_member_permissions"])
            if common_data["default_member_permissions"]
            else None
        )
        if isinstance(cmd, app_commands.Command):
            return cls(
                type=common_data["type"],
                name=cmd.name,
                description=cmd.description,
                default_member_permissions=common_data["default_member_permissions"],
                dm_permission=common_data["dm_permission"],
                nsfw=common_data["nsfw"],
                options=[
                    AppCommandOption.from_parameter(data, param)
                    for data, param in zip(common_data["options"], cmd.parameters)
                ],
                description_localizations={
                    discord.Locale(k): v for k, v in common_data["description_localizations"].items()
                },
                name_localizations={discord.Locale(k): v for k, v in common_data["name_localizations"].items()},
            )
        elif isinstance(cmd, app_commands.ContextMenu):
            return cls(
                type=common_data["type"],
                name=cmd.name,
                description=common_data.get("description", ""),
                default_member_permissions=common_data["default_member_permissions"],
                dm_permission=common_data["dm_permission"],
                nsfw=common_data["nsfw"],
                options=[],
                description_localizations={
                    discord.Locale(k): v for k, v in common_data["description_localizations"].items()
                },
                name_localizations={discord.Locale(k): v for k, v in common_data["name_localizations"].items()},
            )
        return cls(
            type=common_data["type"],
            name=cmd.name,
            description=cmd.description,
            default_member_permissions=common_data["default_member_permissions"],
            dm_permission=common_data["dm_permission"],
            nsfw=common_data["nsfw"],
            options=[AppCommandGroupOption.from_command(data["options"][n], opt) for n, opt in enumerate(cmd.commands)],
            description_localizations={
                discord.Locale(k): v for k, v in common_data["description_localizations"].items()
            },
            name_localizations={discord.Locale(k): v for k, v in common_data["name_localizations"].items()},
        )


class SlashCommandTree(app_commands.CommandTree["CustomBot"]):
    _current_commands_list: list[AppCommandDict]

    async def on_error(self, interaction: Interaction[discord.Client], error: AppCommandError | Exception) -> None:
        if isinstance(error, app_commands.errors.CommandInvokeError):
            error = error.original
        message = f"""
                    \nException: {error.__class__.__name__},
                    Command: {interaction.command.qualified_name if interaction.command else None},
                    User: {interaction.user},
                    Time: {discord.utils.format_dt(interaction.created_at, style='F')}\n
                    """
        try:
            await interaction.response.send_message(f"An error occurred: {message}")
        except discord.InteractionResponded:
            await interaction.followup.send(f"An error occurred: {message}")

    async def _fetch_commands(self) -> List[AppCommand]:
        params = {"with_localizations": int(bool(self.translator))}
        data = await self.client.http.request(
            Route("GET", "/applications/{application_id}/commands", application_id=self.client.user.id),
            params=params,
        )
        return [AppCommand(data=cmd, state=self.client._connection) for cmd in data]

    async def _revalidate_commands(self) -> None:
        if not self.translator:
            self._current_commands_list = [
                AppCommandDict.from_command(cmd.to_dict(), cmd) for cmd in self.get_commands()
            ]
        else:
            self._current_commands_list = [
                AppCommandDict.from_command(await cmd.get_translated_payload(self.translator), cmd)
                for cmd in self.get_commands()
            ]

    async def _sync_commands(self, diff: Diff, *, guild: Snowflake | None = None) -> Diff | None:
        if any((diff.added, diff.removed, diff.updated)):
            self.client.logger.info(f"Detected changes to commands:\n{str(diff)}")
            cmds = await super().sync(guild=guild)
            self.client.logger.info(f"Successfully synced {len(cmds)} commands.")
            return diff
        self.client.logger.info("No changes to commands detected.")
        return None

    async def _sync(self, *, guild: Snowflake | None = None) -> Diff | None:
        _global_commands_list = [AppCommandDict.from_app_command(cmd) for cmd in await self._fetch_commands()]
        await self._revalidate_commands()
        diff = self._app_commands_diff(_global_commands_list, self._current_commands_list)
        return await self._sync_commands(diff, guild=guild)

    async def smart_sync(self, *, guild: Snowflake | None = None) -> Diff | None:
        _old_commands_list = self._current_commands_list.copy()
        await self._revalidate_commands()
        diff = self._app_commands_diff(_old_commands_list, self._current_commands_list)
        return await self._sync_commands(diff, guild=guild)

    def _app_commands_diff(self, old: Sequence[AppCommandDict], new: Sequence[AppCommandDict]) -> Diff:
        old_cmds = {(cmd.name, cmd.type): cmd for cmd in old}
        new_cmds = {(cmd.name, cmd.type): cmd for cmd in new}
        diff = Diff(same=[], added=[], removed=[], updated=[])

        for (name, c_type), new_cmd in new_cmds.items():
            old_cmd = old_cmds.get((name, c_type))
            if old_cmd is None:
                diff.added.append(new_cmd)
            elif old_cmd != new_cmd:
                diff.updated.append(new_cmd)
            else:
                diff.same.append(new_cmd)

        for (name, c_type), old_cmd in old_cmds.items():
            if (name, c_type) not in new_cmds:
                diff.removed.append(old_cmd)

        return diff
