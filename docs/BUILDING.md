# Building and exporting the contribution

Run these commands from this repository's root, using a fresh `build/` directory.
The preparation and export tools refuse to overwrite existing output directories.

## Requirements

- Python >=3.12 and the packages in [tools/requirements.txt](../tools/requirements.txt).
- Git, CMake >=3.21, a C++20 compiler and GNU gettext tools.
- The dependencies in the [upstream development instructions](https://github.com/colobot/colobot/blob/dev/docs/README-dev.md).
  On Debian/Ubuntu, also install `nlohmann-json3-dev` and `libgtest-dev` to use
  system libraries instead of the corresponding submodules.
- On Windows, use MSYS2 UCRT64 with its native compiler, dependencies and Ninja.

## Fetch the upstream sources

```sh
git clone --branch dev https://github.com/colobot/colobot.git build/src/colobot
git clone --branch dev https://github.com/colobot/colobot-data.git build/src/colobot-data
```

The tools read the exact commits from [upstream.json](../upstream.json), rather
than using the current branch tips. Keep the clone history so those commits are
available locally.

## Set up Python

On Linux:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r tools/requirements.txt
```

In a Windows MSYS2 UCRT64 shell:

```sh
export PYTHONUTF8=1
python -m pip install --target build/python-deps -r tools/requirements.txt
export PYTHONPATH="$(cygpath -w "$PWD/build/python-deps")"
```

Keep using the same shell for the commands below.

## Prepare and validate

```sh
python tools/prepare.py --engine build/src/colobot --data build/src/colobot-data --output build/prepared
python tools/validate.py --require-complete --engine build/prepared/colobot --data build/prepared/colobot-data
```

The preparation tool archives the pinned commits into new source trees, copies
the Italian catalogs and updated templates, and applies the engine patch.
The original checkouts are preserved.
With `--require-complete`, validation also checks that every upstream template
directory has an Italian catalog, in addition to checking individual entries.

## Configure

On Linux:

```sh
cmake -S build/prepared/colobot -B build/engine \
  -DCMAKE_BUILD_TYPE=Release -DTESTS=ON -DDESKTOP=OFF -DPORTABLE=ON \
  -DCMAKE_INSTALL_PREFIX="$PWD/build/install"
cmake -S build/prepared/colobot-data -B build/data \
  -DTRANSLATIONS=ON -DMUSIC=OFF \
  -DCOLOBOT_INSTALL_DATA_DIR="$PWD/build/install/data"
```

On Windows/MSYS2:

```sh
cmake -G Ninja -S build/prepared/colobot -B build/engine \
  -DCMAKE_BUILD_TYPE=Release -DTESTS=ON -DDESKTOP=ON \
  -DPORTABLE=ON -DPORTABLE_SAVES=ON \
  -DCMAKE_INSTALL_PREFIX="$(cygpath -m "$PWD/build/install")"
cmake -G Ninja -S build/prepared/colobot-data -B build/data \
  -DTRANSLATIONS=ON -DMUSIC=OFF \
  -DCOLOBOT_INSTALL_DATA_DIR="$(cygpath -m "$PWD/build/install/data")"
```

Windows requires `DESKTOP=ON` to generate `colobot.rc`. Desktop icon generation
tools and Doxygen are optional for this build. The engine can warn about missing
data during configuration; the separate data build is installed below.

`MUSIC=OFF` skips optional music downloads. Missing-music messages during startup
are expected with this configuration.

## Build, test and install

```sh
cmake --build build/engine --parallel 2
cmake --build build/data --parallel 2
ctest --test-dir build/engine --output-on-failure
cmake --install build/engine
cmake --install build/data
```

Check the generated Italian data and localization safeguards:

```sh
python tools/test_complete_data.py --build build/data --source build/prepared/colobot-data
python tools/check_links.py --data-build build/data
python tools/test_code_preservation.py
python tools/test_code_comments.py
python tools/test_localization_checks.py
```

Recorded results and coverage limits are in [TESTING.md](TESTING.md).

## Run the installed game

Run from the installation directory: this portable build resolves data paths
relative to the current working directory. Use a profile separate from any
0.2.2-alpha installation.

On Linux, with an Italian UTF-8 locale available and a graphical session:

```sh
cd build/install
XDG_DATA_HOME="$PWD/xdg" LC_ALL=it_IT.UTF-8 ./colobot -savedir "$PWD/native-profile"
```

On Windows/MSYS2:

```sh
cd build/install
./colobot.exe
```

Select **Italiano** in the game settings to check explicit language selection.

## Export the upstream patches

From the repository root:

```sh
python tools/export_upstream.py --engine build/src/colobot --data build/src/colobot-data --output build/prs
```

| Output | Target repository | Contents |
|---|---|---|
| `build/prs/colobot-italian.patch` | `colobot/colobot` | Native language registration, engine and desktop catalogs, and two language tests. |
| `build/prs/colobot-data-italian.patch` | `colobot/colobot-data` | Italian data catalogs and regenerated `help/cbot` and `help/generic` POT files. |

Apply each patch to its respective repository at the pinned commit. The export
contains only the upstream contribution; this repository's documentation and
helper scripts are not included.
Exported patches use UTF-8 and LF line endings on both Linux and Windows.

## Optional portable Windows test bundle

From the MSYS2 UCRT64 shell, after installing the tested native Windows build:

```sh
python tools/package_windows.py
```

This creates `build/Colobot-Italiano-Windows64.zip` and its SHA256 file. The ZIP
contains the installed game, runtime DLLs and codecs, a fresh Italian profile,
corresponding game/data/translation sources and dependency licenses. Personal
profiles and logs are excluded. The original installation is preserved.
The defaults use `build/install` and `build/prepared`; other locations can be
specified with the options shown by `--help`.

To include music in a build previously configured with `MUSIC=OFF`, run these
commands before packaging; the first command downloads the optional soundtrack:

```sh
cmake -S build/prepared/colobot-data -B build/data -DMUSIC=ON
cmake --build build/data --parallel 2
cmake --install build/data
```

Extract the ZIP to a new folder and double-click `Gioca-in-italiano.cmd` from
Windows Explorer, outside MSYS2, before sharing it. No MSYS2 installation should
be needed on the receiving PC. The package includes sources, so it is larger
than a binary-only bundle. Packaging does not replace this final Windows test.
