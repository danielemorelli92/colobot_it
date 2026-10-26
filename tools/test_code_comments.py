from code_comments import without_comments, comment_spans
from localization_checks import check_translation
source='grab(InFront); // take the new cell\ndrop(EnergyCell); // install it'
target='grab(InFront); // prendi la batteria\ndrop(EnergyCell); // montala'
assert without_comments(source)==without_comments(target)
assert without_comments(source)!=without_comments(target.replace('InFront','Behind'))
assert not list(comment_spans('message("http://example.com");'))
assert not list(comment_spans('message("// not a comment");'))
check_translation('<code>grab(InFront); // take it</code>','<code>grab(InFront); // prendila</code>')
try:check_translation('<code>grab(InFront); // take it</code>','<code>grab(Behind); // prendila</code>')
except ValueError:pass
else:raise AssertionError('Changed executable code accepted')
print('PASS: translated comments accepted; changed instructions rejected; // in strings/URLs preserved.')
