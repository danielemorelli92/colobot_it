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
