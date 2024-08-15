import asyncio
import os
import pathlib
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv


class MyBot(commands.Bot):
    _watcher: asyncio.Task

    def __init__(self, ext_dir: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ext_dir = pathlib.Path(ext_dir)

    async def _load_extensions(self):
        print("Loading extensions...")
        for file in self.ext_dir.rglob("*.py"):
            if file.stem.startswith("_"):
                continue
            try:
                await self.load_extension(".".join(file.with_suffix("").parts))
                print(f"Loaded {file}")
            except commands.ExtensionError as e:
                print(f"Failed to load {file}: {e}")

    async def setup_hook(self):
        await self._load_extensions()
        self._watcher = self.loop.create_task(self._cog_watcher())
        await self.tree.sync()

    async def _cog_watcher(self):
        print("Watching for changes...")
        last = time.time()
        while True:
            extensions: set[str] = set()
            for name, module in self.extensions.items():
                if module.__file__ and os.stat(module.__file__).st_mtime > last:
                    extensions.add(name)
            for ext in extensions:
                try:
                    await self.reload_extension(ext)
                    print(f"Reloaded {ext}")
                except commands.ExtensionError as e:
                    print(f"Failed to reload {ext}: {e}")
            last = time.time()
            await asyncio.sleep(1)


if __name__ == "__main__":
    load_dotenv()
    bot = MyBot("cogs", command_prefix="!", intents=discord.Intents.all())
    bot.run(str(os.getenv("TOKEN")))
