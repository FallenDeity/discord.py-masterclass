# Help Command

The help command is used to display information about the bot and its commands, cogs/extensions, and groups. There are two types of commands:

1. **Prefix/Message Commands**: These are commands that are used by sending a message to the bot. They are of the form `<prefix><command> [arguments]`. For example, `!help` is a prefix command. Your application uses the underlying `on_message` event to handle these commands and discord holds no information about them.
2. **Slash Commands**: These are commands that are registered with discord. They are of the form `/command [arguments]`. Discord holds information about these commands and can provide information about them to users. This means discord can display to users the commands that your application has registered, required arguments, and its description.

`discord.py` by default provides a minimal help command for prefix commands. The help command can be customized to display information about the bot's commands, cogs/extensions, and groups.

In this guide, we will cover how to customize the help command to display information about the bot's commands, cogs/extensions, and groups for prefix commands first and then extend it to display information about slash commands.

## Custom Help Command

`discord.py` has a set of [base classes](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=helpcommand#help-commands) that can be used to create a custom help command.

- [`commands.DefaultHelpCommand`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=helpcommand#defaulthelpcommand): The default help command that comes with `discord.py`. It is a subclass of `commands.HelpCommand` and acts as a basic help command for prefix and hybrid commands.

=== "Default Help Command"
    ![Default Help Command](./assets/examples/help-command/default-help-command.png)

=== "Command Help"
    ![Command Help](./assets/examples/help-command/default-command-help.png)

=== "Group Help"
    ![Group Help](./assets/examples/help-command/default-group-help.png)

=== "Cog Help"
    ![Cog Help](./assets/examples/help-command/default-cog-help.png)

- [`commands.MinimalHelpCommand`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=helpcommand#minimalhelpcommand): Similar to `DefaultHelpCommand` but with a minimalistic design, using plain text instead of code blocks and simplified formatting.

=== "Minimal Help Command"
    ![Minimal Help Command](./assets/examples/help-command/minimal-help-command.png)

=== "Command Help"
    ![Command Help](./assets/examples/help-command/minimal-command-help.png)

=== "Group Help"
    ![Group Help](./assets/examples/help-command/minimal-group-help.png)

=== "Cog Help"
    ![Cog Help](./assets/examples/help-command/minimal-cog-help.png)

- [`commands.HelpCommand`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=helpcommand#helpcommand): The base class for creating custom help commands. It provides methods that can be overridden to customize the help command's behavior. By default, it does nothing and is meant to be subclassed.

### Methods of HelpCommand

The `commands.HelpCommand` class provides the following methods that can be overridden to customize the help command's behavior and utility methods to construct the help message.

| Method                                               | Description                                                                                                                                                        |
|------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `get_bot_mapping()`                                  | Returns a mapping of command and command group objects to their respective cogs/extensions. If a command is not part of any cog/extension, it is mapped to `None`. |
| `get_command_signature(command)`                     | Returns the signature of the command. Example: `!command [arg1] [arg2]`.                                                                                           |
| `command_not_found(string)`                          | Returns a string to display when a command is not found.                                                                                                           |
| `subcommand_not_found(command, string)`              | Returns a string to display when a subcommand under a command group is not found.                                                                                  |
| `filter_commands(commands, *, sort=False, key=None)` | Filters the commands based on the provided parameters. It runs all associated checks with the command and takes into account weather the command is hidden.        |
| `get_destination()`                                  | Returns the destination where the help command information should be sent.                                                                                         |
| `send_error_message(error)`                          | Sends an error message to the destination. For example, the output of `command_not_found()` would be passed here.                                                  |
| `on_help_command_error(ctx, error)`                  | Handles the error that occurs during the execution of the help command.                                                                                            |
| `send_bot_help(mapping)`                             | Sends the help message for the bot. Invoked when no other argument was passed when calling the help command. Example: `!help`.                                     |
| `send_cog_help(cog)`                                 | Sends the help message for a cog/extension. Invoked when a cog/extension name was passed when calling the help command. Example: `!help cog_name`.                 |
| `send_group_help(group)`                             | Sends the help message for a command group. Invoked when a command group name was passed when calling the help command. Example: `!help group_name`.               |
| `send_command_help(command)`                         | Sends the help message for a command. Invoked when a command name was passed when calling the help command. Example: `!help command_name`.                         |

### Customizing the Help Command

To create a custom help command, you need to subclass `commands.HelpCommand` and override the methods you want to customize. Here is an example of a custom help command that displays information about the bot's commands, cogs/extensions, and groups:

```python title="help_command.py"
from typing import Mapping, Optional, List, Any, Iterable

import discord
import humanfriendly
from discord.ext import commands
from discord.ext.commands import Cog, Command, Group

from paginators.advanced_paginator import EmbedCategoryPaginator, CategoryEntry
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
            category_desc = cog_or_group.description if cog_or_group and cog_or_group.description else "No description provided."
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
```
