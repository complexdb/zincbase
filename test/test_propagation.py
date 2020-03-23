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

with kb.dont_propagate():
    assert kb._dont_propagate
    node4.grains += 1

assert kb._dont_propagate == False
assert node4.grains == 4
assert node5.grains == 1

assert kb._MAX_RECURSION == 1
times_called = 0
def cycle_watch_fn(node, prev_value):
    global times_called
    times_called += 1
    for n, edges in node.neighbors:
        kb.node(n).grains += 1
kb.store('connected(node_a, node_a)')
node_a = kb.node('node_a')
node_a.grains = 0
node_a.watch('grains', cycle_watch_fn)
node_a.grains = 1
assert times_called == 2
assert node_a.grains == 2

node_a.grains = 3
assert times_called == 4
assert node_a.grains == 4

kb.set_recursion_limit(2)
node_a.grains = 5
assert times_called == 7
assert node_a.grains == 7

kb = KB()
kb.store('node(node1)', node_attributes=[{'value': 0}])
kb.store('node(node2)', node_attributes=[{'value': 0}])
kb.store('node(node3)', node_attributes=[{'value': 0}])
kb.store('connected(node1, node2)')
kb.store('connected(node2, node3)')
def watch_fn(node, prev_val):
    for n, pred in node.neighbors:
        kb.node(n).value += 1
kb.node('node1').watch('value', watch_fn)
kb.node('node2').watch('value', watch_fn)
kb.node('node1').value += 1
assert kb.node('node1').value == 1
assert kb.node('node2').value == 1
assert kb.node('node3').value == 1
kb.set_propagation_limit(1)
kb.node('node1').value += 1
assert kb.node('node1').value == 2
kb.node('node2').value == 2
kb.node('node3').value == 1

kb = KB()
kb.store('is_linked(a,b)', edge_attributes={'zig': 1})
edge = kb.edge('a', 'is_linked', 'b')
node_a = kb.node('a')
node_b = kb.node('b')
node_a.node_zig = 1
node_b.node_zig = 2
assert edge.zig == 1
was_called = False
def nights_watch(edge, prev_val):
    global was_called
    assert prev_val == 1
    assert edge.nodes[0] == 'a'
    assert edge.nodes[1] == 'b'
    for node in edge.nodes:
        node.node_zig += 1
    was_called = True
edge.watch('zig', nights_watch)
edge.zig += 1
assert edge.zig == 2
assert node_a.node_zig == 2
assert node_b.node_zig == 3
assert was_called

print('All propagation tests passed.')