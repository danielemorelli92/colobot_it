# Native integration test results

Results recorded on 2026-10-28 against the official `dev` commits pinned in
[upstream.json](../upstream.json), with this repository's patch and catalogs.
Reproduction instructions are in [BUILDING.md](BUILDING.md).

## Localization checks

| Check | Result |
|---|---|
| Gettext catalogs | 146 catalogs; 5,188 translated entries; no empty or fuzzy entries. GNU gettext compilation, format checks, Italian plural forms and MO lookups passed. |
| Generated data | All 4,470 data catalog entries found in the generated Italian files. |
| Code and references | 546 code examples, program names and image references checked. Executable code and string literals preserved; example comments translated. |
| SatCom links | 3,550 links across 453 Italian documents resolved, including two named-anchor references. |
| Validation safeguards | Regression checks reject malformed markup, altered executable code and unresolved SatCom links. |
| Patch export | Both exported patches applied successfully to their respective pristine pinned source trees. |

The pinned upstream `help/cbot` and `help/generic` POT files did not include all
current English source text. Both templates were regenerated and are included in
the contribution. Counts above cover the regenerated data, including `searchall`
and loop labels.

## Linux

Environment: Debian 13, GCC 14.2, C++20, CMake 4.4.4 and GNU gettext 0.23.1.

- Release configuration, compilation and installation passed with `TESTS=ON`,
  `DESKTOP=OFF` and `PORTABLE=ON`.
- All 205 enabled CTest tests passed, including the two added tests for the
  Italian language round trip and compatibility of existing language identifiers.
- Native startup was checked with an Italian system locale and with an English
  locale plus explicit `Language.Lang=it`. Both loaded the installed Italian MO
  catalog and completed the first mission's `-scenetest` run with exit code 0.
- The Italian language selector, SatCom and options were visually checked in
  Xvfb with software rendering at 1280×800.

## Windows

Results reported by the contributor from a local Windows 64-bit build using
MSYS2 UCRT64, GCC 16.2.0, CMake 4.4.4 and Python 3.14.9.

- Configuration, engine and data builds, and installation passed with `TESTS=ON`,
  `DESKTOP=ON`, `PORTABLE=ON` and `PORTABLE_SAVES=ON`.
- All 205 enabled CTest tests passed.
- Graphical startup, Italian menus, mission instructions and the CBOT manual
  were checked in game. Screenshots are included in
  [colobot/colobot#1902](https://github.com/colobot/colobot/issues/1902).
- Italian menu selection persisted after closing and restarting the game.
- A manual save in the first mission was created and loaded successfully;
  mission instructions remained available in Italian through F1.

On both platforms, `CBotUT.PublicClasses` and `CBotUT.StringAsArray` were already
disabled upstream and were not executed.

## Scope and limitations

- These are native `it` catalogs under `lang/it/LC_MESSAGES` and Italian `I` data.
  The checks use native Italian language support, without a language-slot mod.
- The Windows build used `MUSIC=OFF`; optional music was not tested. A C++ locale
  fallback warning was observed under MSYS2, while Italian menus and SatCom
  loaded successfully.
- Linux desktop integration and manpages were not built. The desktop PO passed
  gettext validation; Windows executable resources were generated with
  `DESKTOP=ON`.
- Automated checks and the manual checks above do not cover a complete
  playthrough or a linguistic review of every screen.
