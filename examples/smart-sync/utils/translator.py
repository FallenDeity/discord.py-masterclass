from __future__ import annotations

from discord import app_commands
from discord.app_commands.translator import TranslationContextTypes, locale_str
from discord.enums import Locale
from gpytranslate import Translator as GoogleTranslator


class Translator(app_commands.Translator):
    translator = GoogleTranslator()

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContextTypes) -> str | None:
        try:
            translation = await self.translator.translate(string.message, sourcelang="en", targetlang=locale.value)
            return str(translation.text)  # type: ignore
        except Exception:
            return None
