## What are cogs?

Cogs are a way to organize your bot's code into modules. They are a way to keep your code clean and organized, and to prevent your main file from getting too big and messy.

## Difference between Cogs and Extensions

Cog is a class that inherits from `commands.Cog` while extension is a Python module (file) that most of the time contains a Cog and is used to load them into your bot.

### Loading extensions

To load an extension, you use `bot.load_extension()` method.

```python
await bot.load_extension("cogs.super_cog")
```

!!! note "Note"
    The extension path is made almost the same like importing a module. If we had our extension under `cogs/super_cog.py` we would use `cogs.super_cog` as the extension path.

### Unloading extensions

To unload an extension, you use `bot.unload_extension()` method.

```python
await bot.unload_extension("cogs.super_cog")
```

## Register command

To register a command we use `@commands.command()` decorator.

```python
class SuperCog(commands.Cog):
    @commands.command()
    async def super_command(self, ctx: commands.Context):
        ...
```

## Register event

To register an event we use `@commands.Cog.listener()` decorator.

```python
class SuperCog(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ...
```

## Register task

To register a task we use `@tasks.loop()` decorator.

```python
class SuperCog(commands.Cog):
    @tasks.loop(...)
    async def super_task(self):
        ...
```

## Example Extension

```python title="cogs/super_cog.py"
from discord.ext import commands

class SuperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def super_command(self, ctx: commands.Context):
        ...

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ...

    @tasks.loop(...)
    async def super_task(self):
        ...

async def setup(bot):
    await bot.add_cog(SuperCog(bot))
```

Lets break this down.

### `setup` function

This function is used to load the extension into your bot. It is called by the bot when you load the extension.

!!! note "Note"
    This function is required for the extension to work.

### `bot.add_cog` method

This method is used to add the Cog to the bot.

### `SuperCog` class

This is the `Cog` class. It inherits from `commands.Cog` and has a constructor that takes `bot` as an argument. This allows you to access the bot instance within the Cog.

## How to load extensions from a folder

Lets say you have a folder called `cogs` and you want to load all extensions from it.
We can use `os` module to get all files from the folder and then load them.

```python
@bot.event
async def setup_hook():
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")
```

!!! note "Note"
    `file[:-3]` is used to remove `.py` from the file name.

## Managing extensions using commands

### Load extension

```python
@bot.command()
async def load(ctx: commands.Context, extension: str):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension}!")
```

### Reload extension

```python
@bot.command()
async def reload(ctx: commands.Context, extension: str):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded {extension}!")
```

### Unload extension

```python
@bot.command()
async def unload(ctx: commands.Context, extension: str):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded {extension}!")
```

## Cog Groups

`GroupCog` is a `Cog` subclass hence all `Cog` methods are supported. Every command in the Cog will be registered as a subcommand of the group. You can set name of the group using `group_name` metadata option.

```python
class SuperCog(commands.GroupCog, group_name="utility"):
    @commands.command()
    async def ping(self, ctx: commands.Context):
        ...
```
!!! warning "Warning"
    Group Cogs only work with slash commands and hybrid commands. If you define a prefixed command inside it will be defined at root level hence command will be registered as `ping`.

## Advanced settings

### Extensions

#### `teardown` function

This function is called when the extension is being unloaded. It is used to cleanup.

```python
async def teardown(bot):
    print("Extension unloaded!")
```

### Cogs

#### `cog_load` method

This method is called when the Cog is being loaded. It is used to start tasks and do other setup.

```python
class SuperCog(commands.Cog):
    async def cog_load(self):
        print("Cog loaded!")
```

#### `cog_unload` method

This method is called when the Cog is being unloaded. It is used to cancel tasks and do other cleanup.

```python
class SuperCog(commands.Cog):
    async def cog_unload(self):
        print("Cog unloaded!")
```

#### `cog_check` method

This method registers a check that will be used for all commands in the Cog. This method must take `ctx` as an argument.

```python
class SuperCog(commands.Cog):
    async def cog_check(self, ctx: commands.Context):
        return ctx.author.id == 1234567890
```

#### `interaction_check` method

This method registers a check that will be used for all interactions in the Cog. This method must take `interaction` as an argument.

```python
class SuperCog(commands.Cog):
    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == 1234567890
```

#### `cog_before_invoke` method

This method registers a before invoke hook that will be used for all commands in the Cog. This method must take `ctx` as an argument.

```python
class SuperCog(commands.Cog):
    async def cog_before_invoke(self, ctx: commands.Context):
        print("Before invoke!")
```

#### `cog_after_invoke` method

This method registers a after invoke hook that will be used for all commands in the Cog. This method must take `ctx` as an argument.

```python
class SuperCog(commands.Cog):
    async def cog_after_invoke(self, ctx: commands.Context):
        print("After invoke!")
```

### Cogs metadata

#### `name` attribute

This attribute is used to set the name of the Cog. If not set, the name will be the class name.

```python
class SuperCog(commands.Cog, name="Super Cog"):
    ...
```

## Jishaku

Jishaku is a debugging and testing cog for discord.py bots. It is a very useful tool for bot developers. Installation can be found on the following sites.

[Github](https://github.com/Gorialis/jishaku) [PyPi](https://pypi.org/project/jishaku/) [Documentation](https://jishaku.readthedocs.io/en/latest/)
