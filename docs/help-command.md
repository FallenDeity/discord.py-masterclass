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

To create a custom help command, you need to subclass `commands.HelpCommand` and override the methods you want to customize. These customizations can include formatting the help message, altering the help message's appearance, paginating the help message, and handling interactions with the user.

We can divide the customization into two parts:

1. **Formatting the Help Message**: This involves formatting the help message to display relevant information and also to make it visually appealing.
2. **Sending the Help Message**: This involves sending the formatted help message to the user, and handling interactions with the user.

!!! note "Note"
    In this guide, we will be utilizing the pagination classes from the [Pagination](./pagination.md) guide to paginate the help message.

#### Formatter Class

The `Formatter` class is responsible for formatting the help message. It contains methods to format the command signature, help, aliases, cooldown, enabled status, and description. It also contains methods to format the command, cog/extension, and group help messages.

```python title="help_command.py"
from typing import Optional, List

import discord
import humanfriendly
from discord.ext import commands


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
        # command.help is the docstring of the command, might be None.
        return command.help or "No help provided."

    @staticmethod
    def __format_command_aliases(command: commands.Command) -> str:
        # Join the aliases with a comma and space.
        return f"```yaml\nAliases: {', '.join(command.aliases)}```" if command.aliases else "No aliases."

    @staticmethod
    def __format_command_cooldown(command: commands.Command) -> str:
        # Humanfriendly is used to format the cooldown time in a human-readable format.
        # Source: https://github.com/xolox/python-humanfriendly
        return (
            f"Cooldown: {humanfriendly.format_timespan(command.cooldown.per, max_units=2)} per user."
            if command.cooldown
            else "No cooldown set."
        )

    @staticmethod
    def __format_command_enabled(command: commands.Command) -> str:
        return f"Enabled: {command.enabled}" if command.enabled else "Command is disabled."

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
        # Commands or command groups may be created standalone or outside a cog, in which case cog_or_group is None.
        category_name = cog_or_group.qualified_name if cog_or_group else "No Category"
        # Get the description of the cog or group.
        if isinstance(cog_or_group, commands.Group):
            category_desc = cog_or_group.help or "No description provided."
        else:
            # cog_or_group is a Cog object, might be None.
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

        # Create multiple embeds if the number of commands exceeds 5, with 5 commands per embed.
        for i in range(0, len(commands_), 5):
            embed = cog_embed.copy()
            # Create chunks of 5 commands and add them to the embed.
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
```

| Method                       | Description                                                                                                                                                           |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `__format_command_signature` | Formats the command signature. It returns the command name and its signature. For example, `<prefix>command [arg1] [arg2]`.                                           |
| `__format_param`             | Formats the command parameters, arguments, and usage. It returns the command signature. For example, `<arg1>`, `[arg2=default value]`.                                |
| `__format_command_help`      | Returns the command help/description or a default message if no help is provided.                                                                                     |
| `__format_command_aliases`   | Returns the command aliases or a default message if no aliases are provided. For example, `Aliases: alias1, alias2`.                                                  |
| `__format_command_cooldown`  | Returns the command cooldown or a default message if no cooldown is set. For example, `Cooldown: 5 seconds per user`.                                                 |
| `__format_command_enabled`   | Returns the command enabled status or a default message if the command is disabled. For example, `Enabled: True`.                                                     |
| `format_command`             | Formats the command help message, utilizing the above methods.                                                                                                        |
| `format_cog_or_group`        | Formats the cog/extension or group help message, utilizing the above methods. Creates multiple embeds if the number of commands exceeds 5, with 5 commands per embed. |

#### Sending the Help Message

The `CustomHelpCommand` class is responsible for sending the help message. It contains methods we need to override as per our requirements.

Here is a flowchart which visualizes the flow of the help command, and how the methods are called:

![Flowchart](./assets/examples/help-command/flowchart.png)<figcaption>Flowchart of the Help Command. Image credit: [InterStella0](https://gist.github.com/InterStella0/b78488fb28cadf279dfd3164b9f0cf96)</figcaption>

```python title="help_command.py"
from typing import Mapping, Optional, List, Any, Iterable

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Command, Group

from paginators.advanced_paginator import EmbedCategoryPaginator, CategoryEntry
from paginators.button_paginator import EmbedButtonPaginator


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

            # mapping includes a None key for commands that are not part of any cog, we need to check for it.
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

Now let's take a look at how the `CustomHelpCommand` class works:

- `flatten_commands`: For prefix commands, you can build command groups with subcommands. A command group can also have another command group registered under it, hence forming a hierarchy. This method flattens the command groups and returns a list of commands.
- `send_bot_help`: This function receives a mapping or in more simple terms, a dictionary where the key is a `commands.Cog` object and the value is a list of `commands.Command` and `commands.Group` objects. There is also a singular `None` key that holds all the commands that are not part of any cog.
    - The function creates a home page that displays each cog and the number of commands it has, and the `No Category` section for commands that are not part of any cog.
    - It then creates a list of `CategoryEntry` objects, where each object represents a category (cog or `No Category`) and a corresponding list of pages which include a short description for the category and the commands it contains.
    - Finally, it creates an `EmbedCategoryPaginator` object and starts the paginator.
- `send_cog_help`: This function receives a `commands.Cog` object and sends the help message for the cog. It filters the commands of the cog, formats the cog help message, and starts the paginator. Each page contains a maximum of 5 commands.
- `send_group_help`: This function receives a `commands.Group` object and sends the help message for the group. It filters the commands of the group, formats the group help message, and starts the paginator. Each page contains a maximum of 5 commands.
- `send_command_help`: This function receives a `commands.Command` object and sends the help message for the command. It filters the command, formats the command help message, and sends the embed.
- `send_error_message`: This function receives an error message and creates an embed with the error message. It then sends the embed to the user.

=== "Bot Help"
    ![Bot Help Command](./assets/examples/help-command/prefix-bot-help-command.gif)

=== "Cog Help"
    ![Cog Help Command](./assets/examples/help-command/prefix-cog-help-command.gif)

=== "Group Help"
    ![Group Help Command](./assets/examples/help-command/prefix-group-help-command.png)

=== "Command Help"
    ![Command Help Command](./assets/examples/help-command/prefix-command-help-command.png)

=== "Error Message"
    ![Error Message](./assets/examples/help-command/prefix-error-message.png)

## Registering the Custom Help Command

To use the custom help command, you need to register it with the bot. You can do this by passing an instance of the `CustomHelpCommand` class to the `help_command` parameter of the `commands.Bot` constructor.

```python
from discord.ext import commands

from help_command import CustomHelpCommand

bot = commands.Bot(command_prefix="!", help_command=CustomHelpCommand())
```

Now, when you run the bot and use the help command, you will see the custom help message. This will also register your help command under ungrouped or under the `None` key in the mapping.

Alternatively, to avoid this you can register the help command under a cog. This will group the help command under the cog name in the mapping.

```python
from discord.ext import commands

from help_command import CustomHelpCommand


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._help_command = CustomHelpCommand()
        self._help_command.cog = self
        self._original_help_command = bot.help_command
        bot.help_command = self._help_command

    def cog_unload(self):
        self.bot.help_command = self._original_help_command
```

![Help Command in Cog](./assets/examples/help-command/help-command-in-cog.png)

## Slash Help Command

The custom help command we created so far only works for prefix commands. This is because the `mapping`
