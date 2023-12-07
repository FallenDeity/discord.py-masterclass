# Make Directory translations

```bash
mkdir -p translations
```

# Message POT generation

```bash
find . -iname "*.py" | xargs xgettext --from-code=UTF-8 --language=Python -o translations/dpygt.pot --add-comments
```

# Message PO generation

```bash
locales=(id da de en_GB en_US en_ES fr hr it lt hu nl no pl pt_BR ro fi sv_SE vi tr cs el bg ru uk hi th zh_CN ja ko zh_TW)
pot=translations/dpygt.pot
po=translations/locales/%s/LC_MESSAGES/dpygt.po

for locale in ${locales[@]}; do
    mkdir -p $(dirname $(printf $po $locale))
    if [ -f $(printf $po $locale) ]; then
        msgmerge --update --backup=off --no-fuzzy-matching --no-wrap --sort-output $(printf $po $locale) $pot
    else
        msginit --no-translator --locale=$locale --input=$pot --output-file=$(printf $po $locale)
    fi
done
```

# Message MO generation

```bash
find . -iname "*.po" | xargs -I {} sh -c 'msgfmt -o $(dirname {})/$(basename {} .po).mo {}'
```
