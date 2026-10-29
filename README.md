# Colobot: Gold Edition — Italian translation / Traduzione italiana

> **Windows 0.2.2 compatibility branch.** The maintainer contribution remains on
> [main](https://github.com/danielemorelli92/colobot_it/tree/main), targeting `dev`.
> This branch additionally provides `tools/prepare_022.py` and
> `tools/build_windows_022.cmd` for a local MSVC x64 build of the original
> 0.2.2-alpha release with native Italian language selection.
> The `.cmd` file is a five-line CRLF launcher without batch labels. It invokes
> `tools/build_windows_022.py`, whose sequencing, arguments and failure handling
> are checked by `python tools/test_build_windows_022.py` without a compiler.
> Source archives explicitly use LF newlines, as required by the original
> data translation reader. The build phase detects earlier CRLF preparations
> and restores the pinned data sources and Italian catalogs before generation.
> This recovery is checked by `python tools/test_prepare_022.py`.
>
> In an x64 Visual Studio 2022 Developer Command Prompt, with MSYS2 at
> `C:\msys64` and vcpkg revision
> `f6a5d4e8eb7476b8d7fc12a56dff300c1c986131` bootstrapped at
> `C:\colobot-build-022\vcpkg`, run `tools\build_windows_022.cmd configure`,
> then `tools\build_windows_022.cmd build` after successful configuration.
> Configuration completes a shallow vcpkg history when necessary: the pinned
> `libiconv` and `physfs` overrides require historical port trees. It also
> downloads and compiles static dependencies and can take time.
> The library ports stay at the 2023 revision above. The helper updates only
> `vcpkg.exe` to the checksum-verified 2024-06-10 release, which recognizes
> MSVC 14.4 supplied with recent Visual Studio 2022 installations.
> Before CMake runs, six Windows tool archives are downloaded or checked in
> the vcpkg cache against their original SHA512 values. The two 7-Zip 21.07
> archives come from the official `ip7z/7zip` GitHub release because their old
> `7-zip.org` addresses return HTTP 404. `tools\build_windows_022.cmd all`
> configures, builds, validates and installs in sequence, stopping on failure.
> A local overlay of the pinned `boost-modular-build-helper` port adds the
> missing `vc144` to `vc140` filename normalization for MSVC 14.4. Its port
> revision is incremented so dependent Boost libraries are rebuilt with the
> expected names. Boost itself remains at 1.82.0; the registry is preserved.
> The installed MSYS2 UCRT64 `pkgconf.exe` supplies `PKG_CONFIG`, preserved in
> vcpkg's build environment through its supported `VCPKG_KEEP_ENV_VARS` setting.
> This avoids downloading the removed MSYS2 pkgconf 1.8.0 package.
> The three GNU ports (`libiconv`, `gettext-libintl`, `gettext`) also have local
> overlays that reuse the installed MSYS2 environment through a host-tool port.
> This bypasses their complete retired 2023 MSYS2 archive set, leaving vcpkg's
> own scripts and library sources intact. Missing tools are installed with
> `pacman --needed`, including the Automake 1.16 compiler wrapper required by
> the old build scripts. Autoconf 2.71 and Automake 1.16 are selected explicitly.
> Before the library build, a host check compiles, links
> and runs x64 MSVC programs through that wrapper in Release and Debug modes.
> Installed tool versions and the probe result are saved under
> `build/release-022/host-tools-check/verification.json`.
> On a library configuration failure, the script also prints excerpts from
> that library's compiler/configure logs.
> The helper applies the archived native 0.2.2 registration patch and updates
> matching catalog entries from the current translation. It validates all
> 5,172 entries before configuring the build.
> Reusing prepared sources accepts gettext's normal catalog metadata/order
> updates while checking original input hashes and preserving all message
> identifiers, translations and flags.
>
> Build output goes to `C:\colobot-build-022\install`. Music downloads are
> skipped. The MSVC x64 Release build and installation completed successfully
> on Windows on 2026-10-29 using MSVC 19.44.35229. The executable imports only
> Windows system DLLs. All 5,172 catalog entries, 4,455 generated data entries
> and 3,534 SatCom links passed validation. The contributor subsequently
> confirmed that the extracted, clean Italian game works on Windows.
>
> `python tools/package_windows_022.py --original "PATH_TO_ORIGINAL_GAME"`
> creates `C:\colobot-build-022\colobot-gold-0.2.2-alpha-win64-italiano.zip`
> from the installed build and an original official Windows 0.2.2 folder.
> It copies only the 4,255 paths in `tools/windows_022_manifest.txt`, preserves
> original assets, music and existing languages, replaces `colobot.exe`,
> adds 452 Italian help pages and the Italian interface catalog, and inserts
> Italian title/summary lines into 173 level files without changing other lines.
> The playable archive has exactly 4,708 files, with no added runtime DLLs,
> launchers, profiles or development files. Sources, dependency source caches
> and license notices go into a separate `-sources.zip`. Checksums and a
> verification report are written alongside the archives. Packaging is tested
> by `python tools/test_package_windows_022.py`; the original folder is preserved.
>
> After packaging and runtime verification, close the game and MSYS2 terminals.
> Run `python tools/cleanup_windows_022.py --apply` from the repository directory
> to verify both archives, move them to `Desktop/Colobot-Italiano`, extract the
> playable game there, and back up test saves/settings before deleting the
> project build trees, vcpkg checkout and previous MSYS2 test build. The clone,
> unrelated files and normal AppData profiles are retained. Without `--apply`,
> the command only previews the cleanup. It refuses mismatched archives,
> conflicting backup files and linked deletion paths; regression checks are in
> `tools/test_cleanup_windows_022.py`. MSYS2 and Visual Studio Build Tools can
> then be uninstalled through Windows Settings if no other projects need them.
> If the game has already been extracted elsewhere, use
> `python tools/cleanup_windows_022.py --game "PATH_TO_EXTRACTED_GAME" --apply`.
> This checks the complete Italian game and leaves it in place; the game ZIP
> and old verification metadata are optional. A missing source archive is
> recreated and checked from the retained build sources before deleting them.
> The instructions below describe the separate `dev` contribution.

The Windows build uses the MSVC/vcpkg/static configuration documented in the
[official MSVC guide](https://github.com/colobot/colobot/wiki/How-to-Build-Colobot%3A-Gold-Edition-Using-MSVC)
and the [0.2.2 Windows workflow](https://github.com/colobot/colobot/blob/colobot-gold-0.2.2-alpha/.github/workflows/build.yml).
Its old tool downloads require the compatibility measures above on current
Visual Studio and MSYS2 installations. The current `dev` branch instead uses
the upstream `Windows-CI` preset in `CMakePresets.json`; its options differ from
0.2.2 and should not be copied into the release build unchanged.

[English](#english) | [Italiano](#italiano)

## English

Italian translation of the interface, missions and SatCom, prepared for native
integration into the official `dev` branches.

Upstream discussion: [colobot/colobot#1902](https://github.com/colobot/colobot/issues/1902).

### Contribution

- Native **Italiano** language selection: `it`, Italian UTF-8 locale and data
  language code `I`. Existing language identifiers are preserved.
- **146 catalogs and 5,188 translated entries**, with no empty or fuzzy entries
  and both Italian plural forms.
- Translated example comments, with executable code, identifiers and string
  literals preserved.
- Regenerated `help/cbot` and `help/generic` POT files to cover English source
  text missing from the pinned upstream templates.

The upstream commits are pinned in [upstream.json](upstream.json).

### Review and verification

- [Build, validate and export the contribution](docs/BUILDING.md)
- [Recorded Linux and Windows test results and limitations](docs/TESTING.md)
- [Italian terminology and code/markup preservation rules](docs/GLOSSARY.md)
- [Official translation guidelines](https://github.com/colobot/colobot/wiki/Working-with-translations)

Builds and all 205 enabled CTest tests passed on Linux and Windows. Local Windows
checks also covered Italian menus and SatCom, language persistence, and
saving/loading in the first mission. See the test report for the scope of these
checks and the two tests already disabled upstream.

### Repository layout

| Path | Purpose |
|---|---|
| [translations/colobot](translations/colobot) | Engine and desktop Italian catalogs for `colobot/colobot`. |
| [translations/colobot-data](translations/colobot-data) | Italian data catalogs and two updated templates for `colobot/colobot-data`. |
| [patches/colobot-dev-italian.patch](patches/colobot-dev-italian.patch) | Native language registration and two language tests. |
| [tools](tools) | Source preparation, localization checks and export of the two upstream patches. |

### License and provenance

GPL v3 or later, like Colobot and Colobot Data; see [LICENSE](LICENSE).
The translation was prepared with AI assistance and reviewed in game by an
Italian speaker. This repository contains a proposed contribution, not an
official Colobot release.

The community Windows 0.2.2 build and packaging tools are maintained separately
on the [windows-0.2.2 branch](https://github.com/danielemorelli92/colobot_it/tree/windows-0.2.2).

---

## Italiano

Traduzione italiana dell’interfaccia, delle missioni e del SatCom, preparata per
l’integrazione nativa nei rami `dev` ufficiali.

Discussione sul contributo: [colobot/colobot#1902](https://github.com/colobot/colobot/issues/1902).

### Contenuto del contributo

- Selezione nativa di **Italiano**: `it`, locale italiana UTF-8 e codice dei dati
  `I`. Gli identificatori delle lingue esistenti sono preservati.
- **146 cataloghi e 5.188 voci tradotte**, nessuna vuota o fuzzy ed entrambe le
  forme dei plurali italiani.
- Commenti degli esempi tradotti, preservando codice eseguibile, identificatori
  e stringhe dei programmi.
- POT `help/cbot` e `help/generic` rigenerati per includere i testi inglesi
  mancanti nei template dei commit ufficiali fissati.

I commit ufficiali di riferimento sono fissati in [upstream.json](upstream.json).

### Revisione e verifiche

La documentazione tecnica seguente è in inglese per facilitare la revisione dei
manutentori:

- [Compilare, validare ed esportare il contributo](docs/BUILDING.md)
- [Risultati e limiti dei test Linux e Windows](docs/TESTING.md)
- [Terminologia italiana e regole per codice e marcatori](docs/GLOSSARY.md)
- [Linee guida ufficiali per le traduzioni](https://github.com/colobot/colobot/wiki/Working-with-translations)

Compilazione e tutti i 205 test CTest abilitati sono riusciti su Linux e Windows.
Il collaudo locale Windows ha verificato anche menu e SatCom in italiano,
persistenza della lingua e salvataggio/ricaricamento nella prima missione.
Il rapporto dei test descrive l’ambito delle verifiche e i due test già
disabilitati dal progetto ufficiale.

### Struttura della repository

| Percorso | Contenuto |
|---|---|
| [translations/colobot](translations/colobot) | Cataloghi italiani del motore e del desktop per `colobot/colobot`. |
| [translations/colobot-data](translations/colobot-data) | Cataloghi italiani dei dati e due template aggiornati per `colobot/colobot-data`. |
| [patches/colobot-dev-italian.patch](patches/colobot-dev-italian.patch) | Registrazione nativa della lingua e due test delle lingue. |
| [tools](tools) | Preparazione dei sorgenti, controlli della traduzione ed esportazione delle due patch. |

### Licenza e provenienza

GPL v3 o successiva, come Colobot e Colobot Data; vedere [LICENSE](LICENSE).
La traduzione è stata preparata con assistenza AI e revisionata nel gioco da
un utente italofono. Questa repository contiene una proposta di contributo,
non una release ufficiale di Colobot.

Gli strumenti per compilare e impacchettare la versione comunitaria Windows 0.2.2
sono mantenuti separatamente nel [ramo windows-0.2.2](https://github.com/danielemorelli92/colobot_it/tree/windows-0.2.2).
