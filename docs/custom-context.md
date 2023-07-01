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

[Custom context example from discord.py](https://github.com/Rapptz/discord.py/blob/master/examples/custom_context.py)
