# Embeds

## What is Embed?

Discord Embed object is a message component that is used as a way of adding rich content with different structures and formatting styles

## Overview

Here is an example of an embed with all its features.

```py
@bot.command()
async def foo(ctx: commands.Context):
    some_url = "https://fallendeity.github.io/discord.py-masterclass/"
    embed = discord.Embed(
        title="Title",
        description="Description",
        url=some_url,
        color=discord.Color.random(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="Field name", value="Color sets that <")
    embed.add_field(name="Field name", value="Color should be an integer or discord.Colour object")
    embed.add_field(name="Field name", value="You can't set image width/height")
    embed.add_field(name="Non-inline field name", value="The number of inline fields that can shown on the same row is limited to 3", inline=False)
    embed.set_author(name="Author", url=some_url,
                     icon_url="https://cdn.discordapp.com/attachments/1112418314581442650/1124820259384332319/fd0daad3d291ea1d.png")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1028706344158634084/1124822236801544324/ea14e81636cb2f1c.png")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1112418314581442650/1124819948317986926/db28bfb9bfcdd1f6.png")
    embed.set_footer(text="Footer", icon_url="https://cdn.discordapp.com/attachments/1112418314581442650/1124820375587528797/dc4b182a87ecee3d.png")
    await ctx.send(embed=embed)
```

!!! warning "Warning"
    Almost all embed methods require keyword-only arguments

![Showcase](assets/embeds/1.png)

## (De)serialization

Converting embed objects to the Python dictionary and vice versa is very simple.

For that we can use [from_dict](https://discordpy.readthedocs.io/en/stable/api.html?#discord.Embed.from_dict) and [to_dict](https://discordpy.readthedocs.io/en/stable/api.html?#discord.Embed.to_dict) methods

```pycon
>>> import discord
>>> embed = discord.Embed(title="Hello", description="world!")
>>> embed.add_field(name="Field name", value="Field value")
>>> embed_dict = embed.to_dict()
>>> _
{'fields': [{'inline': True, 'name': 'Field name', 'value': 'Field value'}], 'type': 'rich', 'description': 'world!', 'title': 'Hello'}
>>> embed_dict["description"] = "test"
>>> embed = discord.Embed.from_dict(embed_dict)
>>> type(embed)
<class 'discord.embeds.Embed'>
>>> embed.description
'test'
```

## How to create an empty field?

You can't create an empty field due to Discord API restrictions, however you can get around them by using invisible characters

```py
@bot.command()
async def foo(ctx: commands.Context):
    embed = discord.Embed()
    # embed.add_field(name="") -> Error
    embed.add_field(name="\u200b", value="Where is the name?")
    await ctx.send(embed=embed)
```

![Showcase](assets/embeds/2.png)

## How to use local image for an embed image?

!!! info "Note"
    It's a copy from [discord.py faq](https://discordpy.readthedocs.io/en/stable/faq.html#local-image)

Discord special-cases uploading an image attachment and using it within an embed so that it will not display separately, but instead in the embed’s thumbnail, image, footer or author icon.

To do so, upload the image normally with [abc.Messageable.send()](https://discordpy.readthedocs.io/en/stable/api.html#discord.abc.Messageable.send), and set the embed’s image URL to `attachment://image.png`, where `image.png` is the filename of the image you will send.

Quick example:
```py
file = discord.File("path/to/my/image.png", filename="image.png")
embed = discord.Embed()
embed.set_image(url="attachment://image.png")
await channel.send(file=file, embed=embed)
```

## Embed generating website

!!! warning "Warning"
    We don't advise using the website to create embeds: it's best to do it on your own. But it's actually very comfortable.

On this [site](https://cog-creators.github.io/discord-embed-sandbox/) you can generate discord.py code for creating an embed

