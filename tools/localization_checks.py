"""Checks for Colobot's documented pseudo-HTML and native control sequences."""
from collections import Counter
import re

# Angle-bracketed button captions such as <build a ...> are visible prose,
# not control tags. Match the documented grammar, including nested real links.
TAG = re.compile(r'<(?:button|key) [^<>]*/>|<a [^<>]+>|</a>|<format (?:const|type|token|key)>|</format>|</?code>|<(?:const|type|token|norm|key|s|c|b|n)/>')
NATIVE = re.compile(r'\\(?:button|key|u|image|font|size) [^;\n]*;|\\(?:tab|const|type|token|norm|key|s|c|b|n|t|l);')
PRINTF = re.compile(r'%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[diuoxXfFeEgGcs%]')

def markers(text):
    return Counter(TAG.findall(text) + NATIVE.findall(text))

def check_translation(source, target, flags=()):
    if markers(source) != markers(target):
        raise ValueError('Changed Colobot control tags or link targets')
    if 'c-format' in flags and Counter(PRINTF.findall(source)) != Counter(PRINTF.findall(target)):
        raise ValueError('Changed printf arguments')
    # A single backslash separates an interface label from its tooltip.
    # Raw control strings are checked above instead of treating them as tooltips.
    if '\\' in source and not NATIVE.search(source):
        if source.count('\\') != target.count('\\'):
            raise ValueError('Changed label/tooltip separator count')
    if source.count('\t') != target.count('\t'):
        raise ValueError('Changed literal tab indentation')
    if Counter(re.findall(r'<c/>(.*?)<n/>', source, re.S)) != Counter(re.findall(r'<c/>(.*?)<n/>', target, re.S)):
        raise ValueError('Changed native-style code example')
    for code in re.findall(r'<code>.*?</code>', source, re.S):
        if code not in target:
            raise ValueError('Changed CBot code block')
