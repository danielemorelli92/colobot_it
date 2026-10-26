"""Locate CBot // comments without interpreting // inside strings or URLs."""
import re
MARKUP=re.compile(r'<(?:button|key) [^<>]*/>|<a [^<>]+>|</a>|<format (?:const|type|token|key)>|</format>|</?code>|<(?:const|type|token|norm|key|s|c|b|n)/>')
def comment_spans(text):
    offset=0
    for line in text.splitlines(keepends=True):
        quote=None; escaped=False; i=0
        while i<len(line)-1:
            c=line[i]
            if quote:
                if escaped: escaped=False
                elif c=='\\': escaped=True
                elif c==quote: quote=None
            elif c in ('"', "'"):
                quote=c
            elif line[i:i+2]=='//' and (i==0 or line[i-1]!=':'):
                end=len(line.rstrip('\r\n'))
                yield offset+i+2,offset+end
                break
            i+=1
        offset+=len(line)
def without_comments(text):
    for start,end in reversed(list(comment_spans(text))):
        text=text[:start]+''.join(MARKUP.findall(text[start:end]))+text[end:]
    return text
