from __future__ import annotations

import copy
import io
import typing as t

import discord
from discord.ext import commands
from PIL import Image, ImageOps
from views import BaseModal

from . import BaseLayoutView

__all__: tuple[str, ...] = (
    "SubclassedActionRow",
    "ImageFilterView",
)


class SubclassedActionRow(discord.ui.ActionRow["BaseLayoutView"]):
    view: BaseLayoutView

    def __init__(self):
        super().__init__()
        self.add_item(
            discord.ui.Button["BaseLayoutView"](
                label="Contact Support", style=discord.ButtonStyle.link, url="https://support.example.com"
            )
        )

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button["BaseLayoutView"]):
        self.view._disable_all()
        await self.view._edit(view=self.view)
        await interaction.followup.send("Confirmed!", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button["BaseLayoutView"]):
        await interaction.response.send_message("Cancelled!", ephemeral=True)
        self.view._disable_all()
        await self.view._edit(view=self.view)
        await interaction.followup.send("Cancelled!", ephemeral=True)


class ImageFilterActionRow(discord.ui.ActionRow["BaseLayoutView"]):
    view: "ImageFilterView"

    @discord.ui.button(label="Grayscale", style=discord.ButtonStyle.primary)
    async def grayscale(self, interaction: discord.Interaction, button: discord.ui.Button["BaseLayoutView"]):
        await self.view.apply_filter(interaction, lambda img: img.convert("L"))

    @discord.ui.button(label="Sepia", style=discord.ButtonStyle.primary)
    async def sepia(self, interaction: discord.Interaction, button: discord.ui.Button["BaseLayoutView"]):
        def sepia_filter(img: Image.Image) -> Image.Image:
            # The matrix for Sepia transformation
            sepia_matrix = (0.393, 0.769, 0.189, 0, 0.349, 0.686, 0.168, 0, 0.272, 0.534, 0.131, 0)
            return img.convert("RGB").convert("RGB", sepia_matrix)

        await self.view.apply_filter(interaction, sepia_filter)

    @discord.ui.button(label="Sketch", style=discord.ButtonStyle.primary)
    async def sketch(self, interaction: discord.Interaction, button: discord.ui.Button["BaseLayoutView"]):
        def sketch_filter(img: Image.Image) -> Image.Image:
            return img.convert("L").point(lambda x: 255 - x)

        await self.view.apply_filter(interaction, sketch_filter)

    @discord.ui.button(label="Neon", style=discord.ButtonStyle.primary)
    async def neon(self, interaction: discord.Interaction, button: discord.ui.Button["BaseLayoutView"]):
        def negative_filter(img: Image.Image) -> Image.Image:
            return ImageOps.invert(img.convert("RGB"))

        await self.view.apply_filter(interaction, negative_filter)

    @discord.ui.button(label="Solarize", style=discord.ButtonStyle.primary)
    async def solarize(self, interaction: discord.Interaction, button: discord.ui.Button["BaseLayoutView"]):
        def solarize_filter(img: Image.Image) -> Image.Image:
            return ImageOps.solarize(img.convert("RGB"), threshold=128)

        await self.view.apply_filter(interaction, solarize_filter)


class UserActionRow(discord.ui.ActionRow["BaseLayoutView"]):
    view: "ImageFilterView"
    selected_user: discord.User | discord.Member | None = None

    @discord.ui.select(cls=discord.ui.UserSelect, min_values=1, max_values=1)
    async def user_select(self, interaction: discord.Interaction, select: discord.ui.UserSelect["BaseLayoutView"]):
        await interaction.response.defer()
        self.selected_user = select.values[0]
        self.view.media_gallery.clear_items()
        avatar_asset = self.selected_user.display_avatar.with_size(256).with_format("png")
        avatar_bytes = await avatar_asset.read()
        file = discord.File(fp=io.BytesIO(avatar_bytes), filename="avatar.png")
        self.view.media_gallery.add_item(media=file)
        await self.view._edit(view=self.view, attachments=[file])


class ImageFilterView(BaseLayoutView):
    def __init__(
        self, bot: commands.Bot, default_image: discord.File, user: discord.User | discord.Member, timeout: float = 60
    ):
        super().__init__(user, timeout)
        self.bot = bot
        self.image_bytes = default_image.fp.read()
        default_image.fp.seek(0)
        self.media_gallery = discord.ui.MediaGallery["BaseLayoutView"](discord.MediaGalleryItem(media=default_image))
        self.file_attachment = discord.ui.File["BaseLayoutView"](media=default_image)
        # self.user_action_row = UserActionRow()
        # self.user_action_row.selected_user = self.bot.user  # type: ignore
        container = discord.ui.Container["BaseLayoutView"](
            discord.ui.Section(
                "## Image Filter",
                "Select an image filter to apply.",
                accessory=discord.ui.Thumbnail["BaseLayoutView"](media=self.bot.user.display_avatar.url),  # type: ignore
            ),
            self.media_gallery,
            ImageFilterActionRow(),
            # self.user_action_row,
            self.file_attachment,
            accent_color=discord.Color.blurple(),
        )
        self.add_item(container)

    async def apply_filter(
        self, interaction: discord.Interaction, filter_func: t.Callable[[Image.Image], Image.Image]
    ) -> None:
        await interaction.response.defer()
        img_bytes = copy.deepcopy(self.image_bytes)

        def process_image() -> io.BytesIO:
            with Image.open(io.BytesIO(img_bytes)) as img:
                filtered_img = filter_func(img)
                byte_io = io.BytesIO()
                filtered_img.save(byte_io, format="PNG")
                byte_io.seek(0)
                return byte_io

        filtered_image_io = await self.bot.loop.run_in_executor(None, process_image)
        file = discord.File(fp=filtered_image_io, filename="image.png")
        self.media_gallery.clear_items()
        self.media_gallery.add_item(media=file)
        self.file_attachment = discord.ui.File["BaseLayoutView"](file)
        await self._edit(view=self, attachments=[file])


class FileUploadModal(BaseModal, title="Upload a File"):
    def __init__(self, *, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)
        self.file_upload = discord.ui.FileUpload["FileUploadModal"](min_values=1, max_values=1, required=True)
        self.add_item(
            discord.ui.Label(
                text="Upload",
                component=self.file_upload,
                description="You can upload a maximum of 1 file.",
            )
        )
