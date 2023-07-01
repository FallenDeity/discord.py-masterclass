# Custom Context Class

[Context](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?#discord.ext.commands.Context) with it's attributes has a lot of usages, but
sometimes we want to add some more methods/attributes.

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

### Creating custom bot class

* Subclass bot and override `get_context` method to use your context class

```py
class MyBot(commands.Bot):
    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)
```

* Don't forget to use your custom bot, not default one

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