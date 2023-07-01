# Custom Context Class

There are many uses for [context](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?#discord.ext.commands.Context) and its properties, however occasionally we wish to add some additional methods or attributes.

Here is how you do it in discord.py:

### Creating custom context class

* Subclass context and add your features

```py
class MyContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test = 123

    async def send_test(self):
        await self.send(self.test)
```

!!! info "Note"
    You can override any library methods of context if you want.

### Overriding get_context

* Make discord.py use your context class by overriding the [get_context](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?#discord.ext.commands.Bot.get_context) method in the bot subclass.

```py
class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)
```

* Don't forget to use your custom bot class, not default one

```py
bot = MyBot(".", intents=intents)
```

### Creating example command

```py
@bot.command()
async def foo(ctx: MyContext):
    await ctx.send_test()
```

### Result

And that's all! Let's test it now

![Showcase](assets/custom-context/1.png)

### More examples

#### Tick method

!!! info "Note"
    Code was taken from [discord.py examples](https://github.com/Rapptz/discord.py/blob/master/examples/custom_context.py)

Here, we're adding a method called `tick` to the context, which, based on the value provided, adds a cross or a checkmark emoji. 

```py
import random

import discord
from discord.ext import commands


class MyContext(commands.Context):
    async def tick(self, value):
        emoji = '\N{WHITE HEAVY CHECK MARK}' if value else '\N{CROSS MARK}'
        try:
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            pass


class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)


intents = discord.Intents.default()
intents.message_content = True

bot = MyBot('.', intents=intents)


@bot.command()
async def guess(ctx, number: int):
    """Guess a random number from 1 to 6."""
    value = random.randint(1, 6)
    print(value)
    await ctx.tick(number == value)


bot.run("token")
```

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
