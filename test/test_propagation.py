import context

from zincbase import KB
kb = KB()

kb.store('connected(node1, node2)')

node1 = kb.node('node1')

was_called = False
def hello_neighbor(new_neighbor):
    global was_called
    was_called = True
    assert new_neighbor == 'node3'

node1.watch_for_new_neighbor(hello_neighbor)

kb.store('connected(node1, node3)')
assert was_called

node1.grains = 0
def watch_fn(node, prev_val):
    for n, predicate in node.neighbors:
        kb.node(n).grains += 1

node1_watch = node1.watch('grains', watch_fn)
node1 = kb.node('node1')
assert 'grains' in node1._watches

kb.store('connected(node3, node4)')
node2, node3, node4 = kb.node('node2'), kb.node('node3'), kb.node('node4')
node2.grains = 0
node3.grains = 0
node4.grains = 0
node2_watch = node2.watch('grains', watch_fn)
node3_watch = node3.watch('grains', watch_fn)

node1.grains += 1
assert node2.grains == 1
assert node3.grains == 1
assert node4.grains == 1
node3.grains += 1
assert node2.grains == 1
assert node3.grains == 2
assert node4.grains == 2

node4.watch('grains', watch_fn)
kb.store('connected(node4, node5)', node_attributes=[{}, {'grains': 0}])
node5 = kb.node('node5')
node4.grains += 1
assert node4.grains == 3
assert node5.grains == 1

print('All propagation tests passed.')