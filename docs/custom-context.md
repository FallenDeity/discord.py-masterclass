# Custom Context Class

There are many uses for [context](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?#discord.ext.commands.Context) and its properties, however occasionally we wish to add some additional methods or attributes.

Here is how you do it in discord.py:

### Creating custom context class

* Subclass context and add your features

```py
import typing

from discord.ext import commands

class MyContext(commands.Context):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.test = 123

    async def send_test(self):
        await self.send(f"{self.test}")
```

!!! info "Note"
    You can override any library methods of context if you want.

### Overriding get_context

* Make discord.py use your context class by overriding the [get_context](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?#discord.ext.commands.Bot.get_context) method in the bot subclass.

```py
import discord
from discord.ext import commands

class MyBot(commands.Bot):
    async def get_context(self, message: discord.Message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)
```

* Don't forget to use your custom bot class, not default one

```py
bot = MyBot(".", intents=intents)
```

### Creating example command

```py
@bot.command()
async def foo(ctx: MyContext) -> None:
    await ctx.send_test()
```

### Result

![Showcase](assets/custom-context/1.png){ align=left }

And that's it! You can now use your custom context class.

!!! info "Note"
    Custom class context is limited to commands which you `commands.Context` as a required argument. Meaning that you can't use it with slash commands.

### More examples

#### Tick method

Here, we're adding a method called `tick` to the context, which, based on the value provided, adds a cross or a checkmark emoji. 

[:fontawesome-solid-paper-plane: Example from discord.py](https://github.com/Rapptz/discord.py/blob/master/examples/custom_context.py){ .md-button .md-button--primary }

![Showcase](assets/custom-context/2.png)

#### Storing custom attribute for server

Let's create a simple table to hold a guild secret value.

```mysql
CREATE TABLE `test`.`secret` (
  `guild_id` BIGINT UNSIGNED NOT NULL,
  `value` VARCHAR(64) NOT NULL DEFAULT 'nothing',
  PRIMARY KEY (`guild_id`));
```

After that, let's add two methods in the context: one retrieves the value from this table, the other modifies it.

```py
import aiomysql
import discord
from discord.ext import commands


class MyContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_secret_value(self):
        async with aiomysql.connect(...) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT value FROM secret WHERE guild_id = %s", (self.guild.id,))
                data = await cursor.fetchone()
                if data is None:
                    await cursor.execute("INSERT INTO secret (guild_id) VALUES (%s)", (self.guild.id,))
                    await connection.commit()
                    return "nothing"
                return data[0]

    async def set_secret_value(self, new_value):
        async with aiomysql.connect(...) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("UPDATE secret SET value = %s WHERE guild_id = %s", (new_value, self.guild.id))
                await connection.commit()


class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)


intents = discord.Intents.default()
intents.message_content = True

bot = MyBot('.', intents=intents)


@bot.command()
async def get(ctx: MyContext):
    secret = await ctx.get_secret_value()
    await ctx.send(f"||{secret}||")


@bot.command()
async def change(ctx: MyContext, new_value: str):
    await ctx.set_secret_value(new_value)
    await ctx.send(f"Secret value changed")

bot.run("token")
```

![Showcase](assets/custom-context/3.png)