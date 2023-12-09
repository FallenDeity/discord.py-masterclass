import argparse
import codecs
import logging
import re

import polib
from deep_translator import GoogleTranslator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_for_names_and_args(msg_id: str, msg_str: str) -> str:
    string = msg_str
    if " " not in msg_id or "_" in msg_id:
        string = string.replace(" ", "_")
    if msg_id.islower():
        string = string.lower()
    if not any(char in msg_id for char in "'!\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~'"):
        string = re.sub(r"[^\w\s]", "", string)
    return string


def get_target_language(language: str) -> str:
    LANG_MAP = {
        "en_US": "en",
        "en_GB": "en",
        "pt_BR": "pt",
        "zh_CN": "zh-CN",
        "zh_TW": "zh-TW",
        "sv_SE": "sv",
    }
    return LANG_MAP.get(language, language)


def translate_po_file(po_file: str) -> None:
    """Translate a PO file to a target language.

    Args:
        po_file: The PO file to translate.
    """
    po = polib.pofile(po_file, encoding="utf-8")
    target_language = get_target_language(po.metadata["Language"])
    translator = GoogleTranslator(source="en", target=target_language)
    for n, entry in enumerate(po, start=1):
        if entry.msgstr or not entry.msgid:
            entry.msgstr = check_for_names_and_args(entry.msgid, entry.msgstr)
            logger.info(f"{n}/{len(po)}: {entry.msgid} -> {entry.msgstr}")
            continue
        entry.msgstr = translator.translate(entry.msgid)
        entry.msgstr = check_for_names_and_args(entry.msgid, entry.msgstr)
        try:
            entry.msgstr = codecs.decode(entry.msgstr.encode("utf-8"), "utf-8")
        except UnicodeEncodeError:
            logger.warning(f"Entry {entry.msgid} could not be encoded in {target_language}")
            entry.msgstr = ""
        logger.info(f"{n}/{len(po)}: {entry.msgid} -> {entry.msgstr}")
    logger.info(f"Removing obsolete entries: {[entry.msgid for entry in po if entry.obsolete or entry.fuzzy]}")
    new_entries = [entry for entry in po if not entry.obsolete and not entry.fuzzy]
    po.clear()
    po.extend(new_entries)
    po.save()
    # po.save_as_mofile(po_file.replace(".po", ".mo"))


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "po_file",
        help="The PO file to translate.",
    )
    args = parser.parse_args()
    translate_po_file(args.po_file)


if __name__ == "__main__":
    main()
