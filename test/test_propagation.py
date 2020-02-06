import context

from zincbase import KB
kb = KB()

kb.store('connected(node1, node2)')

node1 = kb.node('node1')

def hello_neighbor(new_neighbor):
    assert new_neighbor == 'node3'

node1.watch_for_new_neighbor(hello_neighbor)

kb.store('connected(node1, node3)')

print('All propagation tests passed.')