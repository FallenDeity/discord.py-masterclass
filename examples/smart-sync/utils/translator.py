from __future__ import annotations

import gettext
import logging
import typing
from pathlib import Path
from typing import Iterator

import discord
from discord import app_commands

_LOCALES_PATH = Path("translations/locales")
DOMAIN = "dpygt"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def locale_to_gnu(locale: discord.Locale) -> str:
    return str(locale).replace("-", "_")


def yield_mo_paths() -> Iterator[Path]:
    log.info(f"Looking for compiled localizations in {_LOCALES_PATH}")
    if not _LOCALES_PATH.is_dir():
        return
    for locale in _LOCALES_PATH.iterdir():
        lc_messages = locale / "LC_MESSAGES"
        if not lc_messages.is_dir():
            continue
        log.info(f"Found compiled localizations in {lc_messages}")
        yield from lc_messages.glob("*.mo")


class EmptyTranslations(gettext.NullTranslations):
    """Returns an empty message to indicate no translation is available."""

    def gettext(self, message: str) -> str:
        return ""

    def ngettext(self, msgid1: str, msgid2: str, n: int) -> str:
        return ""

    def pgettext(self, context: str, message: str) -> str:
        return ""

    def npgettext(self, context: str, msgid1: str, msgid2: str, n: int) -> str:
        return ""


class GettextTranslator(app_commands.Translator):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)

        if not any(yield_mo_paths()):
            log.warning("No compiled localizations detected")

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContextTypes,
    ) -> str | None:
        try:
            t = gettext.translation(
                domain=DOMAIN,
                localedir=str(_LOCALES_PATH),
                languages=(locale_to_gnu(locale), "en_US"),
            )
            log.info(f"Using compiled localizations for {locale}")
        except OSError:
            return

        t.add_fallback(EmptyTranslations())

        plural: str | None = string.extras.get("plural")
        if plural is not None:
            assert isinstance(context.data, int)
            translated = t.ngettext(string.message, plural, context.data)
        else:
            translated = t.gettext(string.message)
        log.info(f"Translated {string.message} to {translated}")
        return translated or None
