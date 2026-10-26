#!/usr/bin/env python3
"""Package an optional French-slot preview for the unmodified official Windows game."""
from pathlib import Path
import argparse
import gettext
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import zipfile
import polib

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--data-build', type=Path, required=True)
p.add_argument('--data-source', type=Path, required=True)
p.add_argument('--msgfmt', default='msgfmt')
p.add_argument('--output', type=Path, required=True)
a=p.parse_args()
a.output.parent.mkdir(parents=True,exist_ok=True)
files={}
def add(path, text):
    assert path not in files, path
    files[path]=text.encode('utf-8') if isinstance(text,str) else text
base='colobot-it-preview/'
# Refuse stale data builds: catalog messages must agree with generated outputs.
subprocess.run([sys.executable, str(ROOT/'tools/test_generated.py'), str(a.data_build)], check=True)
subprocess.run([sys.executable, str(ROOT/'tools/test_complete_data.py'), '--build', str(a.data_build), '--source', str(a.data_source)], check=True)
subprocess.run([sys.executable, str(ROOT/'tools/test_code_preservation.py')], check=True)
catalogs=[polib.pofile(str(path)) for path in (ROOT/'translations').rglob('it.po')]
translated_count=sum(len(po.translated_entries()) for po in catalogs)
total_count=sum(len(po) for po in catalogs)
assert translated_count == total_count
assert not any(po.fuzzy_entries() for po in catalogs)
# Official generated scenes: preserve gameplay, replace only the French labels
# with the generated Italian labels. The original game has no LANGUAGE_ITALIAN.
scenes=0
for src in sorted((a.data_build/'levels/po').rglob('*.txt')):
    rel=src.relative_to(a.data_build/'levels/po')
    if src.name in ('scene.txt','chaptertitle.txt'):
        text=src.read_text()
        assert re.search(r'^(Title|Resume|ScriptName)\.I\b',text,re.M),src
        text=re.sub(r'^(?:Title|Resume|ScriptName)\.F[^\n]*(?:\n|$)','',text,flags=re.M)
        text=re.sub(r'^(Title|Resume|ScriptName)\.I\b',r'\1.F',text,flags=re.M)
        original=(a.data_source/'levels'/rel).read_text()
        def gameplay(s):
            return re.sub(r'^(?:Title|Resume|ScriptName)\.[A-Z][^\n]*(?:\n|$)', '', s, flags=re.M)
        assert gameplay(original)==gameplay(text), ('Gameplay changed', rel)
        add(base+'mod/levels/'+rel.as_posix(),text)
        scenes+=1
    elif src.name.endswith('.I.txt'):
        dest=rel.with_name(src.name.replace('.I.txt','.F.txt'))
        add(base+'mod/levels/'+dest.as_posix(),src.read_bytes())
# Official generator's I/ subtree maps directly to the game's F/ help subtree.
for category in (a.data_build/'help/po').iterdir():
    for src in sorted((category/'I').rglob('*.txt')):
        add(base+'mod/help/F/'+src.relative_to(category/'I').as_posix(),src.read_bytes())
with tempfile.TemporaryDirectory() as temp:
    mo=Path(temp)/'colobot.mo'
    subprocess.run([a.msgfmt,'--check','--check-format','-o',str(mo),str(ROOT/'translations/colobot/po/it.po')],check=True)
    add(base+'lang/fr/LC_MESSAGES/colobot.mo',mo.read_bytes())
    translated=gettext.GNUTranslations(io.BytesIO(mo.read_bytes()))
    assert translated.gettext('Missions')=='Missioni'
add(base+'mod/manifest.txt','DisplayName text="Italiano - anteprima 0.3 (slot French)"\nVersion text="0.3"\nSummary text="Cataloghi italiani completi per 0.2.2-alpha. Usa French solo in questa anteprima."\n')
# This file is a template copied on first launch; it never replaces existing saves.
add(base+'config-iniziale.ini','[Language]\nLang=fr\n\n[Mods]\nNames=mod\nEnabled=1\n')
launcher=r'''@echo off
setlocal
set "GAME_ROOT=%~dp0"
set "PREVIEW_ROOT=%~dp0colobot-it-preview"
if not exist "%GAME_ROOT%colobot.exe" (
  echo Estrai questo pacchetto nella cartella che contiene colobot.exe.
  pause
  exit /b 1
)
if not exist "%GAME_ROOT%data\" (
  echo Cartella data non trovata accanto a colobot.exe.
  echo Questo avvio richiede la distribuzione ufficiale portatile 0.2.2-alpha.
  pause
  exit /b 1
)
set "PREVIEW_SAVE=%LOCALAPPDATA%\ColobotItalianPreview-0.1"
if not defined LOCALAPPDATA (
  echo Variabile LOCALAPPDATA non disponibile.
  pause
  exit /b 1
)
if not exist "%PREVIEW_SAVE%\" mkdir "%PREVIEW_SAVE%"
if not exist "%PREVIEW_SAVE%\colobot.ini" copy /y "%PREVIEW_ROOT%\config-iniziale.ini" "%PREVIEW_SAVE%\colobot.ini" >nul
pushd "%PREVIEW_SAVE%"
"%GAME_ROOT%colobot.exe" -datadir "%GAME_ROOT%data" -langdir "%PREVIEW_ROOT%\lang" -mod "%PREVIEW_ROOT%\mod" -savedir "%PREVIEW_SAVE%"
set "GAME_EXIT=%ERRORLEVEL%"
popd
if not "%GAME_EXIT%"=="0" (
  echo Il gioco e' terminato con codice %GAME_EXIT%.
  echo I file di prova si trovano in "%PREVIEW_SAVE%".
  pause
)
exit /b %GAME_EXIT%
'''
add('Avvia-Italiano.cmd',launcher.replace('\n','\r\n').encode('ascii'))
add('LEGGIMI-ITALIANO.txt','''COLOBOT GOLD 0.2.2-alpha WIN64 - ANTEPRIMA ITALIANA 0.3

1. Chiudi il gioco.
2. Estrai TUTTO questo ZIP nella cartella che contiene colobot.exe e data.
   Devono comparire Avvia-Italiano.cmd e la cartella colobot-it-preview.
3. Fai doppio clic su Avvia-Italiano.cmd.
4. Apri Missioni, Terra, prima missione: Equipaggiamento.
   Campagna principale, interfaccia e aiuto generale sono ora tradotti.
   Se aggiorni dalla 0.1 o 0.2, sostituisci i file dell'anteprima.
   Conserva la cartella dei salvataggi: la 0.3 riutilizza quella precedente.

NON copiare file nella cartella lang originale. Non sostituire l'eseguibile.
L'anteprima usa un catalogo separato e una mod tramite le opzioni ufficiali.
Per funzionare con il gioco originale usa temporaneamente lo slot French:
e' normale vedere French nelle impostazioni. Non scegliere Italiano, che
il binario ufficiale non riconosce. Se cambi lingua, torna a French.

Il launcher crea configurazione e salvataggi separati in:
%LOCALAPPDATA%\\ColobotItalianPreview-0.1
I tuoi salvataggi normali non sono importati: e' normale non vederli qui.
Il launcher non modifica i file originali del gioco.
Per giocare normalmente, avvia il tuo consueto colobot.exe.
Per rimuovere l'anteprima elimina Avvia-Italiano.cmd, colobot-it-preview
e LEGGIMI-ITALIANO.txt. La cartella separata di salvataggi si puo' conservare.

COPERTURA E LIMITI
Interfaccia: 659/659; campagna principale: 878/878.
Aiuto generale: 141/141; robot: 176/176; oggetti ed edifici: 323/323.
I conteggi comprendono identificatori e frammenti di codice lasciati invariati.
Completati anche esercizi, sfide, battaglie, livelli aggiuntivi, CBOT e manuale.
5172/5172 voci compilate nei 146 cataloghi; nessuna vuota o fuzzy.
Non e' una revisione linguistica finale: il collaudo completo nel gioco resta da fare.
Nessun nuovo eseguibile. Completati i testi dei cataloghi della release.
Nomi di programmi, codice, commenti degli esempi e crediti restano invariati.
Le descrizioni di mod esterne e i metadati dell'addon AltTextures non sono cataloghi del gioco.
Catalogo gettext, testi generati, marcatori e struttura del pacchetto verificati
in Linux. Il funzionamento di base della 0.1 e' stato confermato su Windows
dall’utente. Anche la 0.2 e' stata avviata su Windows dall’utente. La 0.3 e' da collaudare.
Se non parte o i testi restano francesi, conserva il messaggio di errore e
segnala il contenuto della finestra e la disposizione delle cartelle.

LICENZA E SORGENTI
GNU GPL v3 o successiva, come i progetti originali.
Vedi colobot-it-preview/LICENZA-GPL3.txt e SORGENTI.txt.
''')
add(base+'LICENZA-GPL3.txt',(a.data_source/'LICENSE.txt').read_bytes())
add(base+'SORGENTI.txt','''Basi ufficiali Colobot: Gold Edition (GPL v3 o successiva):
https://github.com/colobot/colobot/tree/e3addd66f6613174c1a61c373808046e7d49b320
https://github.com/colobot/colobot-data/tree/910b0dd8cf722b0bafbdfe9a506a1ca21f0b8f06
I file dati sono generati dai POT/PO ufficiali con le nuove traduzioni italiane.
I cataloghi modificati e gli script di preparazione e confezionamento sono
inclusi in sources/. I file generati sono testo leggibile nella cartella mod/.
La modifica per questo pacchetto rimappa I in F, senza cambiare la logica
originale dei livelli. L'eseguibile ufficiale non e' incluso o modificato.
Per ricostruire i dati seguire sources/README.md; per lo ZIP eseguire
package_windows_preview.py --data-build <build dati> --data-source <dati ufficiali>
--output <file.zip>. Richiede Python e GNU gettext.
''')
for folder in ['translations','tools','docs']:
    for src in sorted((ROOT/folder).rglob('*')):
        if src.is_file() and '__pycache__' not in src.parts:
            add(base+'sources/'+src.relative_to(ROOT).as_posix(),src.read_bytes())
add(base+'sources/README.md',(ROOT/'README.md').read_bytes())
add(base+'sources/patches/colobot-0.2.2-alpha-italian.patch',(ROOT/'patches/colobot-0.2.2-alpha-italian.patch').read_bytes())
add(base+'COPERTURA.json', json.dumps({'version':'0.3','entries':total_count,'nonempty_entries':translated_count,'untranslated':total_count-translated_count},indent=2)+'\n')
# Inspect the actual archive after writing; no Windows launch is claimed.
manifest={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
add(base+'SHA256SUMS.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in sorted(files.items()): z.writestr(name,data)
with zipfile.ZipFile(a.output) as z:
    assert z.testzip() is None
    for name,digest in manifest.items(): assert hashlib.sha256(z.read(name)).hexdigest()==digest
    scene=z.read(base+'mod/levels/missions/chapter001/level001/scene.txt').decode()
    assert 'Title.F text="Equipaggiamento"' in scene
    assert not re.search(r'^(Title|Resume|ScriptName)\.I\b',scene,re.M)
    assert len(re.findall(r'^Title.F\b',scene,re.M))==1
    assert 'Dal centro di addestramento della NASA' in z.read(base+'mod/levels/missions/chapter001/level001/help/help.F.txt').decode()
print(f'PASS archive: {len(files)} files, {scenes} scene/chapter files; {a.output.stat().st_size} bytes')
print(hashlib.sha256(a.output.read_bytes()).hexdigest())
