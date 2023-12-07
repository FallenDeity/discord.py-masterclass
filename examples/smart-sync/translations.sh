#!/bin/bash

translation_dir=translations
domain=dpygt

mkdir -p $translation_dir/locales

find . -iname "*.py" | xargs xgettext --from-code=UTF-8 --language=Python -o $translation_dir/$domain.pot

locales=(hi fr)
pot=$translation_dir/$domain.pot
po=$translation_dir/locales/%s/LC_MESSAGES/$domain.po

for locale in ${locales[@]}; do
    mkdir -p $(dirname $(printf $po $locale))
    if [ -f $(printf $po $locale) ]; then
        msgmerge --update --backup=off --no-fuzzy-matching --no-wrap --sort-output $(printf $po $locale) $pot
    else
        msginit --no-translator --locale=$locale --input=$pot --output-file=$(printf $po $locale)
    fi
done

find . -iname "*.po" | xargs -I {} sh -c 'msgfmt -o $(dirname {})/$(basename {} .po).mo {}'
