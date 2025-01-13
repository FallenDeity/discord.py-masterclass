import copy
import difflib
import functools
import inspect
import re
from typing import Any, Callable, Dict, Generator, Iterable, List, Mapping, Optional

import discord
import humanfriendly
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog, Command, CommandError, Context, Group
from discord.ext.commands.core import get_signature_parameters
from discord.ext.commands.parameters import Parameter, Signature
from paginators.advanced_paginator import CategoryEntry, EmbedCategoryPaginator
from paginators.button_paginator import EmbedButtonPaginator


class _InjectorCallback:
    def __init__(self, original_callback: Any, bind: "CustomHelpCommand") -> None:
        self.callback = original_callback
        self.bind = bind

    async def invoke(self, *args: Any, **kwargs: Any) -> Any:
        if self.bind.cog is not None:
            cog, *args = args

        return await self.callback.__func__(self.bind, *args, **kwargs)


def _inject_callback(inject):
    try:
        inject.__original_callback__
    except AttributeError:
        inject.__original_callback__ = _InjectorCallback(inject.command_callback, inject)

    caller = inject.__original_callback__
    original_callback = caller.callback

    async def wrapper(*args, **kwargs):
        return await caller.invoke(*args, **kwargs)

    callback = copy.copy(wrapper)
    signature = list(Signature.from_callable(original_callback).parameters.values())
    callback.__signature__ = Signature.from_callable(callback).replace(parameters=signature)
    inject.command_callback = callback


def _parse_params_docstring(func: Callable[..., Any]) -> dict[str, str]:
    doc = inspect.getdoc(func)
    if doc is None:
        return {}

    param_docs = {}
    sphinx_pattern = re.compile(r"^\s*:param\s+(\S+).*?:\s*(.+)", re.MULTILINE)
    google_pattern = re.compile(r"^\s*(\S+)\s*\(.*?\):\s*(.+)", re.MULTILINE)
    numpy_pattern = re.compile(r"^\s*(\S+)\s*:\s*.*?\n\s*(.+?)(?=\n\S|\Z)", re.DOTALL | re.MULTILINE)

    for pattern in (sphinx_pattern, google_pattern, numpy_pattern):
        for match in pattern.finditer(doc):
            param_name, desc = match.groups()
            param_docs[param_name] = desc
    return param_docs


def _construct_full_name(command: commands.Command | app_commands.Command) -> str:
    parent: Optional[app_commands.Group] = command.parent
    entries = []
    while parent is not None:
        entries.append(parent.name)
        parent = parent.parent
    entries.reverse()
    entries.append(command.name)
    return " ".join(entries)


class _HelpHybridCommandImpl(commands.HybridCommand):
    def __init__(self, inject: "CustomHelpCommand", *args: Any, **kwargs: Any) -> None:
        _inject_callback(inject)
        super().__init__(inject.command_callback, *args, **kwargs)
        self._original: "CustomHelpCommand" = inject
        self._injected: "CustomHelpCommand" = inject
        self.params: Dict[str, Parameter] = get_signature_parameters(
            inject.__original_callback__.callback, globals(), skip_parameters=1
        )

        # get function params descriptions, from the original callback docstring
        param_descs = _parse_params_docstring(inject.__original_callback__.callback)
        if self.app_command:
            app_params = [p for p in self.app_command.parameters if p.name in param_descs]
            app_commands.describe(**{p.name: param_descs[p.name] for p in app_params})(self.app_command)

        self.params.update(
            (name, param.replace(description=desc))
            for name, desc in param_descs.items()
            if (param := self.params.get(name))
        )

        self.__inject_callback_metadata(inject)

    def __inject_callback_metadata(self, inject: "CustomHelpCommand") -> None:
        if not self.with_app_command:
            return
        autocomplete = inject.help_command_autocomplete
        self.autocomplete(list(dict.fromkeys(self.params))[-1])(autocomplete)

    async def prepare(self, ctx: Context[Any]) -> None:
        self._injected = injected = self._original.copy()
        injected.context = ctx
        self._original.__original_callback__.bind = injected  # type: ignore
        self.params = get_signature_parameters(injected.__original_callback__.callback, globals(), skip_parameters=1)

        # get function params descriptions, from the original callback docstring
        param_descs = _parse_params_docstring(injected.__original_callback__.callback)
        self.params.update(
            (name, param.replace(description=desc))
            for name, desc in param_descs.items()
            if (param := self.params.get(name))
        )

        on_error = injected.on_help_command_error
        if not hasattr(on_error, "__help_command_not_overridden__"):
            if self.cog is not None:
                self.on_error = self._on_error_cog_implementation
            else:
                self.on_error = on_error

        await super().prepare(ctx)

    async def _on_error_cog_implementation(self, _, ctx: Context[commands.Bot], error: CommandError) -> None:
        await self._injected.on_help_command_error(ctx, error)

    def _inject_into_cog(self, cog: Cog) -> None:
        # Warning: hacky

        # Make the cog think that get_commands returns this command
        # as well if we inject it without modifying __cog_commands__
        # since that's used for the injection and ejection of cogs.
        def wrapped_get_commands(
            *, _original: Callable[[], List[Command[Any, ..., Any]]] = cog.get_commands
        ) -> List[Command[Any, ..., Any]]:
            ret = _original()
            ret.append(self)
            return ret

        # Ditto here
        def wrapped_walk_commands(
            *, _original: Callable[[], Generator[Command[Any, ..., Any], None, None]] = cog.walk_commands
        ):
            yield from _original()
            yield self

        functools.update_wrapper(wrapped_get_commands, cog.get_commands)
        functools.update_wrapper(wrapped_walk_commands, cog.walk_commands)
        cog.get_commands = wrapped_get_commands
        cog.walk_commands = wrapped_walk_commands
        self.cog = cog

    def _eject_cog(self) -> None:
        if self.cog is None:
            return

        # revert back into their original methods
        cog = self.cog
        cog.get_commands = cog.get_commands.__wrapped__
        cog.walk_commands = cog.walk_commands.__wrapped__
        self.cog = None


class Formatter:
    def __init__(self, help_command: commands.HelpCommand) -> None:
        self.ctx = help_command.context
        self.help_command = help_command

    def __format_command_signature(self, command: commands.Command | app_commands.Command) -> tuple[str, str]:
        params = self.help_command.get_command_signature(command)
        return f"{command.qualified_name}\n", f"```yaml\n{params}```"

    @staticmethod
    def __format_param(param: app_commands.Parameter | commands.Parameter) -> str:
        result = (
            f"{param.name}={param.default}"
            if not param.required and param.default is not discord.utils.MISSING and param.default not in (None, "")
            else f"{param.name}"
        )
        result = f"[{result}]" if not param.required else f"<{result}>"
        if isinstance(param, commands.Parameter):
            return f"```yaml\n{param.name} ({param.annotation.__name__}) - {result}:\n\t{param.description}```"
        choices = (
            ", ".join(f"'{choice.value}'" if isinstance(choice.value, str) else choice.name for choice in param.choices)
            if param.choices
            else ""
        )
        result = f"{param.name} ({param.type.name}) - {result}:"
        result += f"\n\t{param.description}" if param.description else ""
        result += f"\n\tChoices: {choices}" if choices else ""
        return f"```yaml\n{result}```"

    @staticmethod
    def __format_command_help(command: commands.Command | app_commands.Command) -> str:
        return command.description or "No help provided."

    @staticmethod
    def __format_command_aliases(command: commands.Command | app_commands.Command) -> str:
        if isinstance(command, app_commands.Command):
            return "No aliases."
        return f"```yaml\nAliases: {', '.join(command.aliases)}```" if command.aliases else "No aliases."

    @staticmethod
    def __format_command_cooldown(command: commands.Command | app_commands.Command) -> str:
        if isinstance(command, app_commands.Command):
            return "No cooldown set."
        return (
            f"Cooldown: {humanfriendly.format_timespan(command.cooldown.per, max_units=2)} per user."
            if command.cooldown
            else "No cooldown set."
        )

    @staticmethod
    def __format_command_enabled(command: commands.Command | app_commands.Command) -> str:
        if isinstance(command, app_commands.Command):
            return "Command is enabled."
        return f"Enabled: {command.enabled}" if command.enabled else "Command is disabled."

    def format_command(self, command: commands.Command | app_commands.Command) -> discord.Embed:
        signature = self.__format_command_signature(command)
        embed = discord.Embed(
            title=signature[0],
            description=signature[1] + self.__format_command_help(command),
            color=discord.Color.blue(),
        )

        params = command.parameters if isinstance(command, app_commands.Command) else command.params.values()
        # format each parameter of the command
        for param in params:
            embed.add_field(
                name=param.name,
                value=self.__format_param(param),
                inline=False,
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
        self,
        cog_or_group: Optional[commands.GroupCog | app_commands.Group | commands.Cog | commands.Group],
        commands_: List[commands.Command | commands.Group | app_commands.Command | app_commands.Group],
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
    __original_callback__: _InjectorCallback

    def __init__(
        self,
        *,
        name: str = "help",
        description: str = "Shows this message",
        with_app_command: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.with_app_command = with_app_command
        self.command_attrs["with_app_command"] = with_app_command
        self.command_attrs["name"] = name
        self.command_attrs["description"] = description
        self._command_impl = _HelpHybridCommandImpl(self, **self.command_attrs)

    def _add_to_bot(self, bot: commands.bot.BotBase) -> None:
        command = _HelpHybridCommandImpl(self, **self.command_attrs)
        self._command_impl = command
        bot.add_command(command)

    def _remove_from_bot(self, bot: commands.bot.BotBase) -> None:
        impl = self._command_impl
        bot.remove_command(impl.name)
        app = impl.app_command
        for snowflake in getattr(app, "_guild_ids", None) or []:
            bot.tree.remove_command(app.name, guild=discord.Object(snowflake))
        impl._eject_cog()

    def get_command_signature(
        self, command: commands.Command[Any, ..., Any] | app_commands.Command[Any, ..., Any]
    ) -> str:
        if isinstance(command, commands.Command):
            return super().get_command_signature(command)

        command_path = _construct_full_name(command)

        def _format_param(data: str, *, required: bool = False) -> str:
            return f"<{data}>" if required else f"[{data}]"

        params = []
        for param in command.parameters:
            # check for attachment type
            if param.type == discord.AppCommandOptionType.attachment:
                params.append(_format_param(f"{param.name} (upload a file)", required=param.required))
                continue

            choices = (
                "|".join(
                    f"'{choice.value}'" if isinstance(choice.value, str) else choice.name for choice in param.choices
                )
                if param.choices
                else ""
            )
            default = (
                f"={param.default}"
                if not param.required and param.default is not discord.utils.MISSING and param.default not in (None, "")
                else ""
            )

            # format name, choices, and default
            formatted = f"{param.name}{default} ({choices})" if choices else f"{param.name}{default}"
            params.append(_format_param(formatted, required=param.required))

        return f"/{command_path} {' '.join(params)}"

    @staticmethod
    def flatten_commands(
        commands_: Iterable[commands.Command | commands.Group | app_commands.Command | app_commands.Group],
    ) -> List[app_commands.Command | commands.Command]:
        flattened = []
        for command in commands_:
            if isinstance(command, commands.Group | app_commands.Group):
                flattened.extend(CustomHelpCommand.flatten_commands(command.commands))
            else:
                flattened.append(command)
        return flattened

    async def send_bot_help(
        self, mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any] | app_commands.Command[Any, ..., Any]]], /
    ) -> None:
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

    async def send_cog_help(self, cog: commands.GroupCog | commands.Cog, /) -> None:
        cmds = cog.get_commands() + (cog.get_app_commands() if self.with_app_command else [])
        if isinstance(cog, commands.GroupCog):
            cmds.extend(cog.app_command.commands)
        commands_ = await self.filter_commands(self.flatten_commands(cmds), sort=True)
        embeds = await Formatter(self).format_cog_or_group(cog, commands_)
        paginator = EmbedButtonPaginator(self.context.author, pages=embeds)
        await paginator.start_paginator(self.context)

    async def send_group_help(self, group: Group[Any, ..., Any] | app_commands.Group, /) -> None:
        commands_ = await self.filter_commands(self.flatten_commands(group.commands), sort=True)
        embeds = await Formatter(self).format_cog_or_group(group, commands_)
        paginator = EmbedButtonPaginator(self.context.author, pages=embeds)
        await paginator.start_paginator(self.context)

    async def send_command_help(self, command: Command[Any, ..., Any] | app_commands.Command[Any, ..., Any], /) -> None:
        embed = Formatter(self).format_command(command)
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

    async def command_callback(self, ctx: commands.Context[commands.Bot], /, *, query: Optional[str] = None) -> None:
        """
        This is the entry point of the help command.

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation.
        query: Optional[str]
            The command, group, or cog to get help for.
        """
        command = query
        await self.prepare_help_command(ctx, command)

        bot = ctx.bot

        if command is None:
            mapping = self.get_all_commands()
            return await self.send_bot_help(mapping)

        cog = bot.get_cog(command)
        if cog:
            return await self.send_cog_help(cog)

        maybe_coro = discord.utils.maybe_coroutine

        keys = command.split()
        cmd = bot.all_commands.get(keys[0])

        if self.with_app_command:
            guild_id = ctx.guild.id if ctx.guild else None

            if cmd is None:
                cmd = bot.tree.get_command(keys[0], guild=discord.Object(id=guild_id))

            if cmd is None:
                cmd = bot.tree.get_command(keys[0])

        if cmd is None:
            string = await maybe_coro(self.command_not_found, self.remove_mentions(command))
            return await self.send_error_message(string)

        for key in keys[1:]:
            try:
                cmds = getattr(cmd, "all_commands", None) or cmd._children
                found = cmds.get(key) if cmds else None
            except AttributeError:
                string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))  # type: ignore
                return await self.send_error_message(string)
            else:
                if found is None:
                    string = await maybe_coro(self.subcommand_not_found, cmd, self.remove_mentions(key))  # type: ignore
                    return await self.send_error_message(string)
                cmd = found

        if isinstance(cmd, commands.Group | app_commands.Group):
            return await self.send_group_help(cmd)
        return await self.send_command_help(cmd)

    def get_all_commands(
        self,
    ) -> Mapping[Optional[Cog], List[Command[Any, ..., Any] | app_commands.Command[Any, ..., Any]]]:
        mapping = self.get_bot_mapping()
        if self.with_app_command:
            for cog, cmds in self.get_app_command_mapping().items():
                for cmd in cmds:
                    if cmd.name not in (c.name for c in mapping.get(cog, [])):
                        mapping.setdefault(cog, []).append(cmd)
        return mapping

    def get_app_command_mapping(
        self,
    ) -> Mapping[Optional[Cog], List[app_commands.Command[Any, ..., Any] | app_commands.Group]]:
        mapping = {}
        for cog in self.context.bot.cogs.values():
            if isinstance(cog, commands.GroupCog):
                mapping.setdefault(cog, [*cog.get_commands()]).extend(cog.app_command.commands)
                continue
            mapping.setdefault(cog, []).extend(cog.get_app_commands())

        # Get unbound commands
        def get_unbound_cmds(with_guild=None):
            return [
                c
                for c in self.context.bot.tree.get_commands(guild=with_guild)
                if isinstance(c, app_commands.Command) and c.binding is None
            ]

        if self.context.guild:
            mapping.setdefault(None, []).extend(get_unbound_cmds(self.context.guild))

        mapping.setdefault(None, []).extend(get_unbound_cmds())

        return mapping

    async def on_help_command_error(self, ctx: Context[commands.Bot], error: CommandError, /) -> None:
        await self.send_error_message(str(error))
        raise error

    async def help_command_autocomplete(
        self, inter: discord.Interaction[commands.Bot], current: str
    ) -> list[app_commands.Choice[str]]:
        help_command = self.copy()
        help_command.context = await inter.client.get_context(inter)

        all_cmds: dict[str, list[commands.Command | app_commands.Command]] = {
            cog.qualified_name if cog else "No Category": help_command.flatten_commands(cmds)
            for cog, cmds in help_command.get_all_commands().items()
        }
        choices = list(all_cmds.keys()) + [_construct_full_name(cmd) for cmd in sum(all_cmds.values(), [])]
        matches = difflib.get_close_matches(current, choices, n=25, cutoff=0.4) or sorted(
            choices, key=lambda x: x.lower()
        )
        return [app_commands.Choice(name=match, value=match) for match in matches][:25]

    async def filter_commands(
        self,
        commands: Iterable[Command[Any, ..., Any] | app_commands.Command[Any, ..., Any]],
        /,
        *,
        sort: bool = False,
        key: Optional[Callable[[Command[Any, ..., Any] | app_commands.Command[Any, ..., Any]], Any] | None] = None,
    ) -> List[Command[Any, ..., Any] | app_commands.Command[Any, ..., Any]]:
        if sort and key is None:
            key = lambda c: c.name  # noqa: E731

        iterator = commands if self.show_hidden else filter(lambda c: not getattr(c, "hidden", None), commands)

        if self.verify_checks is False:
            # if we do not need to verify the checks then we can just
            # run it straight through normally without using await.
            return sorted(iterator, key=key) if sort else list(iterator)  # type: ignore # the key shouldn't be None

        if self.verify_checks is None and not self.context.guild:
            # if verify_checks is None and we're in a DM, don't verify
            return sorted(iterator, key=key) if sort else list(iterator)  # type: ignore

        # if we're here then we need to check every command if it can run
        async def predicate(cmd: Command[Any, ..., Any] | app_commands.Command) -> bool:
            ctx = self.context
            if isinstance(cmd, Command):
                try:
                    return await cmd.can_run(ctx)
                except discord.ext.commands.CommandError:
                    return False

            no_interaction = ctx.interaction is None
            if not cmd.checks and no_interaction:
                binding = cmd.binding
                if cmd.parent is not None and cmd.parent is not binding:
                    return False  # it has group command interaction check

                if binding is not None:
                    check = getattr(binding, "interaction_check", None)
                    if check:
                        return False  # it has cog interaction check

                return True

            if no_interaction:
                return False

            try:
                return await cmd._check_can_run(ctx.interaction)
            except app_commands.AppCommandError:
                return False

        ret = []
        for cmd in iterator:
            valid = await predicate(cmd)
            if valid:
                ret.append(cmd)

        if sort:
            ret.sort(key=key)
        return ret
