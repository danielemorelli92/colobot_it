# Italian translation and native language support

Hi! I would like to contribute Italian support, following the workflow in
[#1124](https://github.com/colobot/colobot/issues/1124).

The [source repository](https://github.com/danielemorelli92/colobot_it) contains
146 Italian gettext catalogs with 5,188 populated entries and no untranslated
or fuzzy entries. They cover the interface, levels, SatCom and example-program
comments. The translation was prepared with AI assistance and reviewed in game
by an Italian-speaking user.

Native integration for `dev` is prepared: **Italiano** in the language menu,
`it` catalogs, Italian UTF-8 locale and `I` for generated data, preserving the
existing language identifiers. Two stale help POTs have also been regenerated
to include the current English documentation, including `searchall`.

Linux build and installation pass, along with 205 unit tests and checks for
catalogs, generated data, code preservation and SatCom links. The installed
application loads Italian through both system-locale detection and explicit
language selection; the native interface and SatCom have been checked visually.
[Validation details and limitations](https://github.com/danielemorelli92/colobot_it/blob/main/docs/VERIFICHE.md).
A community package for Windows 0.2.2-alpha has been tested; native Windows
`dev` testing remains outstanding.

The sources are available under GPLv3-or-later. Would you welcome two coordinated
pull requests targeting `dev`, one for `colobot` and one for `colobot-data`?
