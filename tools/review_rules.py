"""Explicit corrections to upstream help; never permit arbitrary code/link edits."""
# These paths do not resolve to the intended page in the pinned upstream help.
LINK_CORRECTIONS = {
    '<a object|Huston>': '<a object|huston>',
    '<a cbot|convert>': '<a object|convert>',
    '<a cbot|radar()>': '<a cbot|radar>',
    '<a |object\\radar>': '<a object|radar>',
    '<a cbot|bool>float</a>': '<a cbot|float>float</a>',
}
# These are descriptive captions styled as code, not CBot instructions.
PROSE_CODE_CORRECTIONS = {
    '<code>this_is_a_label: while ( true )\n{\n\t</code>Instructions ...<c/>\n}': '<code>this_is_a_label: while ( true )\n{\n\t</code>Istruzioni ...<c/>\n}',
    '<code>< no archive picture available  ></code>': '<code>< nessuna immagine d’archivio disponibile ></code>',
    '<code><a cbot|bloc>bloc</a></code>': '<code><a cbot|bloc>blocco</a></code>',
    '<code><a cbot|pointer>reference</a></code>': '<code><a cbot|pointer>riferimento</a></code>',
    '<code><a cbot|pointer>Reference</a></code>': '<code><a cbot|pointer>Riferimento</a></code>',
    '<code><a cbot|function>functions</a></code>': '<code><a cbot|function>funzioni</a></code>',
}
# Correct only this complete prose entry: the upstream appendix repeats "w"
# instead of "a". No executable example or other "w" literal is exempted.
APPEND_MODE_SOURCE = ('<code>"r"</code> mode: open for reading.\n'
                      '<code>"w"</code> mode: open for writing.\n'
                      '<code>"w"</code> mode: open for appending.')

def reviewed_source(source):
    if source == APPEND_MODE_SOURCE:
        source = source.rsplit('<code>"w"</code>', 1)[0] + '<code>"a"</code> mode: open for appending.'
    for before, after in {**LINK_CORRECTIONS, **PROSE_CODE_CORRECTIONS}.items():
        source = source.replace(before, after)
    return source
