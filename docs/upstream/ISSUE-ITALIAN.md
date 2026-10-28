# Italian translation and native language support

Hi! I would like to contribute an Italian translation of Colobot: Gold Edition.
I am following the translation workflow described in #1124, the Brazilian
Portuguese contributions (#1167 and colobot/colobot-data#36), and the
[translation documentation](https://github.com/colobot/colobot-data/blob/dev/README.i18n.md).

An Italian community package for the official **0.2.2-alpha Windows 64-bit**
release has been completed and accepted by an Italian-speaking tester.
The translation was prepared with AI assistance and checked in the game by
the tester; this is not a claim of an independent line-by-line human review
of every catalog entry.

## Translation scope

- 146 gettext catalogs with 5,172 populated entries, no empty or fuzzy entries,
  including both Italian plural forms where required.
- Interface and desktop/manual catalog, campaign, exercises, challenges,
  code battles, free play, additional missions and SatCom documentation.
- Example-program comments translated, while executable code, identifiers,
  program names and string literals are preserved.
- 700 entries are intentionally identical to the source, including code,
  image references, proper names and credits.

The community package uses an isolated French-slot overlay to work with the
unmodified released executable. For an upstream contribution, the intention
is to add **native Italian support**, rather than contribute that launcher
or overlay workaround.

## Current upstream comparison

A comparison on 28 October 2026 against these `dev` commits found all 5,172
existing entry keys reusable and just one new untranslated entry:

- Engine: `5c0fb16bb8caeba0e6bc27c700bc9119e1bcd03f`.
- Data: `3efb490881a1e297666ac92d5530ee94114d08c2`.

The new entry warns about opening a save file created with a different game
version. This is an exact comparison of `msgctxt`, `msgid` and plural keys,
not a completed migration or native integration test. The comparison will
need refreshing when preparing the pull requests.

## Proposed contribution

Following #1124, I would prepare two coordinated pull requests targeting `dev`:

1. **colobot**: native Italian registration and language-menu entry, `it.po`
   for the interface and desktop/manual catalog, locale/catalog lookup and
   build/install integration.
2. **colobot-data**: Italian PO catalogs for levels and help, using the matching
   generated help-language code (`I`). I would verify consistency with the
   engine, following the language-code collision discussed in #1124.

The intended identifiers are `it` for the catalogs, an Italian UTF-8 locale
where applicable, and `I` for generated help/level files. Existing language
identifiers and enum values would be preserved. A few fixes to broken links
and documentation typos inherited from the English source are recorded
separately and can be split out if preferred.

## Validation already performed on the release-based package

- GNU gettext `--check --check-format`, MO lookups and plural forms.
- Official data-generation build, with all 4,455 data-catalog entries found
  in the generated Italian output.
- Control markers, key/button references, code and scene-logic preservation.
- 3,534 SatCom hyperlinks across 452 Italian documents, including named anchors.
- Basic Windows use and acceptance reported by the tester.

A complete native `dev` engine build, CTest run, Italian locale/catalog loading,
installation and native menu/rendering tests remain to be done. No exhaustive
Windows checklist run is claimed. The current release-based development
build could not configure the full engine because OpenGL development files
were missing.

The contribution would use the projects' GPLv3-or-later licensing terms.
Would maintainers welcome these coordinated Italian-language PRs, and is there
any preferred review or submission process beyond the documented workflow?
