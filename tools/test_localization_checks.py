#!/usr/bin/env python3
from localization_checks import check_translation
check_translation('<build a <a object|factory>bot factory</a>>', '<costruisci una <a object|factory>fabbrica di robot</a>>')
check_translation('98.84% favorable', 'favorevole al 98,84%')
check_translation(r'Play\Start mission!', r'Gioca\Avvia la missione!')
for source,target,flags in [
    ('<a object|factory>bot factory</a>', '<a object|research>fabbrica</a>', ()),
    ('<button 160/>', '<button 163/>', ()),
    ('<key help/>', '<key prog/>', ()),
    ('<code>move(10);</code>', '<code>muovi(10);</code>', ()),
    ('%s %d', '%s %s', ('c-format',)),
    (r'Play\Start mission!', 'Gioca', ()),
    ('<c/>move(10);<n/>', '<c/>muovi(10);<n/>', ()),
    ('\tmove(10);', r'\tmove(10);', ()),
]:
    try: check_translation(source,target,flags)
    except ValueError: pass
    else: raise AssertionError((source,target))
print('PASS: translated bracketed prose accepted; changed link/button/key/code/printf/tooltip rejected.')
# The RC review permits only enumerated upstream errata and prose captions.
check_translation('<a object|Huston>Houston</a>', '<a object|huston>Houston</a>')
check_translation('<code><a cbot|pointer>reference</a></code>', '<code><a cbot|pointer>riferimento</a></code>')
for source, target in [
    ('<a object|Huston>Houston</a>', '<a object|human>Houston</a>'),
    ('<code>reference();</code>', '<code>riferimento();</code>'),
    ('<code>"w"</code>', '<code>"a"</code>'),
    (r'Notes\m notes;', r'Note\m other;'),
]:
    try: check_translation(source, target)
    except ValueError: pass
    else: raise AssertionError((source, target))
print('PASS: explicit upstream errata accepted; arbitrary code, literals and anchors protected.')
