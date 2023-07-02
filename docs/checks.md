# Checks

## What are checks?

[Checks](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?#checks) are utility decorators that are called before to the execution of commands.

These checks should be predicates that take in a single parameter taking a Context. If the check returns a False-like value then during invocation a
CheckFailure exception is raised.

If an exception should be thrown in the predicate then it should be a subclass of CommandError. Any exception not subclassed from it will be propagated.

## How to use?

Check is only a function that, based on the input, either throws an error or returns True/False.

You can apply them on your command by using [commands.check](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?#discord.ext.commands.check)
or [commands.check_any](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?#discord.ext.commands.check_any) decorator

## Built-in checks

You may view all of discord.py's relevant checks in the [documentation](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?#checks).

Let's check some of them!

### has_permissions

Checks if the member has all of the permissions necessary.

```py
@bot.command()
@commands.has_permissions(manage_messages=True)
async def test(ctx):
    await ctx.send('You can manage messages.')
```

!!! info "Note"
this check operates on the current channel permissions, not the guild wide permissions

### has_guild_permissions

Similar to `has_permissions()`, but operates on guild wide permissions instead of the current channel permissions.

### has_any_role

Checks if the member invoking the command has any of the roles specified. This means that if they have one out of the three roles specified, then this check
will return True.

```py
@bot.command()
@commands.has_any_role('Library Devs', 'Moderators', 492212595072434186)
async def cool(ctx):
    await ctx.send('You are cool indeed')
```

### dm_only

Check that indicates this command must only be used in a DM context. Only private messages are allowed when using the command.

```py
@bot.command()
@commands.dm_only()
async def where(ctx):
    await ctx.send('We are in the dm')
```

### guild_only

Check that indicates this command must only be used in a guild context only. Basically, no private messages are allowed when using the command.

```py
@bot.command()
@commands.guild_only()
async def where(ctx):
    await ctx.send('We are in the guild')
```

### is_owner

Checks if the person invoking this command is the owner of the bot.

This is powered by [Bot.is_owner()](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?#discord.ext.commands.Bot.is_owner).

```py
@bot.command()
@commands.is_owner()
async def test(ctx):
    await ctx.send('Hello, creator!')
```

## Creating Custom checks

### is_me

Creating a basic check to see if the command invoker is you.

```py
def check_if_it_is_me(ctx):
    return ctx.message.author.id == 85309593344815104


@bot.command()
@commands.check(check_if_it_is_me)
async def only_for_me(ctx):
    await ctx.send('I know you!')
```

### safe_content

Checks if there are no banned words in the command's message content

```py
banwords = {"rabbit", "horse"}


async def safe_content(ctx):
    return not (set(ctx.message.content.lower().split()) & banwords)


@bot.command()
@commands.check(safe_content)
async def check_content(ctx):
    await ctx.send("Content is clean!")
```

## Extending checks

A special attribute named `predicate` is bound to the value returned
by [commands.check](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?#discord.ext.commands.check) decorator to retrieve the predicate passed to
the decorator.

```py
def owner_or_permissions(**perms):
    original = commands.has_permissions(**perms).predicate

    async def extended_check(ctx):
        if ctx.guild is None:
            return False
        return ctx.guild.owner_id == ctx.author.id or await original(ctx)

    return commands.check(extended_check)
```

This will create a check that uses `commands.has_permissions` with our custom check together to determine whether the user is the guild owner or he has the
required permissions.