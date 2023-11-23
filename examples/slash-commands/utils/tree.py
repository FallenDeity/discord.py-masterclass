from __future__ import annotations

import discord
from discord import app_commands
from discord.app_commands.errors import AppCommandError
from discord.interactions import Interaction


class SlashCommandTree(app_commands.CommandTree):
    async def on_error(self, interaction: Interaction[discord.Client], error: AppCommandError | Exception) -> None:
        if isinstance(error, app_commands.errors.CommandInvokeError):
            error = error.original
        message = f"""
                    \nException: {error.__class__.__name__},
                    Command: {interaction.command.qualified_name if interaction.command else None},
                    User: {interaction.user},
                    Time: {discord.utils.format_dt(interaction.created_at, style='F')}\n
                    """
        try:
            await interaction.response.send_message(f"An error occurred: {message}")
        except discord.InteractionResponded:
            await interaction.followup.send(f"An error occurred: {message}")
