import context

from zincbase import KB
kb = KB('localhost', 6379, 2)
kb.reset()

kb.store('linked(a,b)')
edge = kb.edge('a', 'linked', 'b')
edge.strength = 2
assert edge['strength'] == 2
assert edge.attrs == {'strength': 2}

del kb
kb = KB('localhost', 6379, 2)
edge = kb.edge('a', 'linked', 'b')
assert edge.strength == 2

print('All edge tests passed.')