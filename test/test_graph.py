import context
from zincbase import KB

kb = KB()
kb.store('a(b,c)')
kb.node('b')['is_letter'] = 1.0
assert kb.node('b').attrs == {'is_letter': 1.0}
assert 'is_letter' in kb.node('b')
kb.node('b')['is_letter'] = 2.0
del kb.node('b')['is_letter']
assert 'is_letter' not in kb.node('b').attrs
kb.node('b')['is_letter'] = 2.0
assert kb.node('b').attrs == {'is_letter': 2.0}
kb.edge('b', 'a', 'c').both_alpha = 1.0
assert kb.edge('b', 'a', 'c').attrs == {'both_alpha': 1.0}
kb.edge('b', 'a', 'c')['both_alpha'] = 2.0
assert kb.edge('b', 'a', 'c').attrs == {'both_alpha': 2.0}
assert kb.to_triples() == [('b', 'a', 'c')]
triples = kb.to_triples(data=True)
assert triples == [('b', 'a', 'c', {'is_letter': 2.0}, {'both_alpha': 2.0}, {}, False)]
kb.node('c').is_letter = 0.9
triples = kb.to_triples(data=True)
assert triples == [('b', 'a', 'c', {'is_letter': 2.0}, {'both_alpha': 2.0}, {'is_letter': 0.9}, False)]
neg_rule_idx = kb.store('~a(b,c)')
triples = kb.to_triples(data=True)
assert triples == [('b', 'a', 'c', {'is_letter': 2.0}, {'both_alpha': 2.0}, {'is_letter': 0.9}, True)]
kb.delete_rule(neg_rule_idx)
triples = kb.to_triples(data=True)
assert triples == [('b', 'a', 'c', {'is_letter': 2.0}, {'both_alpha': 2.0}, {'is_letter': 0.9}, False)]
kb.edge('b', 'a', 'c').truthiness = -1
triples = kb.to_triples(data=True)
assert triples == [('b', 'a', 'c', {'is_letter': 2.0}, {'both_alpha': 2.0, 'truthiness': -1}, {'is_letter': 0.9}, True)]
del kb.edge('b', 'a', 'c')['truthiness']
triples = kb.to_triples(data=True)
assert triples == [('b', 'a', 'c', {'is_letter': 2.0}, {'both_alpha': 2.0}, {'is_letter': 0.9}, False)]
edge = kb.edge('b', 'a', 'c')
assert edge['both_alpha'] == 2.0
assert 'both_alpha' in edge.attrs
del edge['both_alpha']
assert 'both_alpha' not in edge.attrs
edge['both_alpha'] = 1.0
assert 'both_alpha' in edge.attrs
assert edge.attrs['both_alpha'] == 1.0

was_called = False
def nights_watch(edge, prev_val):
    global was_called
    assert prev_val == 1.0
    was_called = True
edge.watch('both_alpha', nights_watch)
edge['both_alpha'] = 2.0
assert was_called == True
assert edge.attrs['both_alpha'] == 2.0
assert edge['both_alpha'] == 2.0

kb.store('edge(a,b)')
edge = kb.edge('a', 'edge', 'b')
assert str(edge) == 'a___edge___b'
assert edge.pred == 'edge'
assert edge.nodes == ['a', 'b']
edge.resistance = 3
assert edge.resistance == 3
assert edge['resistance'] == 3
was_called = False
def test_good_stuff(edge, prev_val):
    global was_called
    assert prev_val == 3
    assert edge.resistance == 4
    was_called = True
edge.watch('resistance', test_good_stuff)
edge.resistance += 1
assert was_called
assert 'resistance' in edge.attrs
assert 'resistance' in edge
del edge['resistance']
assert 'resistance' not in edge.attrs
assert 'resistance' not in edge

try:
    kb.node('no_exist')
    assert False
except KeyError:
    assert True

try:
    kb.edge('hello', 'i', 'no_exist')
    assert False
except KeyError:
    assert True

print('All graph tests passed.')