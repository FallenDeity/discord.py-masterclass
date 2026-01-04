# Our objectives:
# - Create a view that handles errors
# - Create a view that disables all components after timeout
# - Make sure that the view only processes interactions from the user who invoked the command

from __future__ import annotations

import traceback
import typing as t

import discord
from discord.ui.select import Select


class BaseLayoutView(discord.ui.LayoutView):
    interaction: discord.Interaction | None = None
    message: discord.Message | None = None

    def __init__(self, user: discord.User | discord.Member, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        # We set the user who invoked the command as the user who can interact with the view
        self.user = user

    # make sure that the view only processes interactions from the user who invoked the command
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("You cannot interact with this view.", ephemeral=True)
            return False
        # update the interaction attribute when a valid interaction is received
        self.interaction = interaction
        return True

    def _disable_all(self) -> None:
        # disable all components
        # so components that can be disabled are buttons and select menus, walk because items can be nested inside containers and action rows
        for item in self.walk_children():
            if isinstance(item, discord.ui.Button) or isinstance(item, Select):
                item.disabled = True

    # after disabling all components we need to edit the message with the new view
    # now when editing the message there are two scenarios:
    # 1. the view was never interacted with i.e in case of plain timeout here message attribute will come in handy
    # 2. the view was interacted with and the interaction was processed and we have the latest interaction stored in the interaction attribute
    async def _edit(self, *args: t.Any, **kwargs: t.Any) -> None:
        if self.interaction is None and self.message is not None:
            # if the view was never interacted with and the message attribute is not None, edit the message
            await self.message.edit(*args, **kwargs)
        elif self.interaction is not None:
            try:
                # if not already responded to, respond to the interaction
                await self.interaction.response.edit_message(*args, **kwargs)
            except discord.InteractionResponded:
                # if already responded to, fetch the original response and edit it
                self.message = await self.interaction.original_response()
                await self.message.edit(*args, **kwargs)

    # to handle errors we first notify the user that an error has occurred and then disable all components
    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item[BaseLayoutView]
    ) -> None:
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        message = f"An error occurred while processing the interaction for {str(item)}:\n```py\n{tb}\n```"
        # disable all components
        self._disable_all()
        # edit the message with the error message
        self.add_item(discord.ui.TextDisplay(message))
        await self._edit(view=self)
        # stop the view
        self.stop()

    async def on_timeout(self) -> None:
        # disable all components
        self._disable_all()
        # edit the message with the new view
        await self._edit(view=self)
