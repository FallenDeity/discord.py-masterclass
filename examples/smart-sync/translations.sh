#!/bin/bash

translation_dir=translations
domain=dpygt

mkdir -p $translation_dir/locales

echo "Generating $domain.pot"
find . -iname "*.py" | xargs xgettext --from-code=UTF-8 --language=Python -o $translation_dir/$domain.pot
sed -i 's/CHARSET/UTF-8/' $translation_dir/$domain.pot

locales=(id da de en_GB en_US es_ES fr hr it lt hu nl no pl pt_BR ro fi sv_SE vi tr cs el bg ru uk hi th zh_CN ja ko zh_TW)
pot=$translation_dir/$domain.pot
po=$translation_dir/locales/%s/LC_MESSAGES/$domain.po

echo "Generating .po files"
for locale in ${locales[@]}; do
    mkdir -p $(dirname $(printf $po $locale))
    if [ -f $(printf $po $locale) ]; then
        msgmerge --update --backup=none --no-fuzzy-matching --no-wrap --sort-output --force-po $(printf $po $locale) $pot
    else
        msginit --no-translator --locale=$locale --input=$pot --output-file=$(printf $po $locale)
    fi
done

echo "Translating .po files"
for locale in ${locales[@]}; do
    echo $(printf $po $locale)
    python -m translator $(printf $po $locale)
done

echo "Compiling .mo files"
find . -iname "*.po" | xargs -I {} sh -c 'msgfmt -o $(dirname {})/$(basename {} .po).mo {}'
