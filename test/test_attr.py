import context

from zincbase import KB

kb = KB()
kb.seed(555)

kb.store('person(tom)')
kb.store('person(shamala)')
kb.store('knows(tom, shamala)')
assert kb.neighbors('tom') == [('shamala', [{'pred': 'knows'}])]

kb.node('tom')['grains'] = 0

tom = kb.node('tom')
assert tom.grains == 0
assert tom.i_dont_exist is None
assert tom['i_dont_exist'] is None

kb.node('shamala').grains = 4
shamala = kb.node('shamala')
assert 'grains' in shamala
assert 'grains' in shamala.attrs
assert shamala.grains == 4
shamala.grains += 1
assert shamala.grains == 5
assert shamala['grains'] == 5
shamala['grains'] += 1
assert shamala['grains'] == 6

kb.store('person(jeraca)')
kb.node('jeraca').grains = 3

zero_grains = list(kb.filter(lambda x: x['grains'] == 0))
assert len(zero_grains) == 1
assert zero_grains[0] == 'tom'
assert zero_grains[0] != 'shamala'

zero_anything = list(kb.filter(lambda x: x['anything'] == 0))
assert len(zero_anything) == 0

more_grains = kb.filter(lambda x: x['grains'] >= 3)
assert next(more_grains) in ['shamala', 'jeraca']
assert next(more_grains) in ['shamala', 'jeraca']

more_grains = kb.filter(lambda x: x['grains'] >= 3, candidate_nodes=['shamala'])
as_list = list(more_grains)
assert as_list == ['shamala']

more_grains = kb.filter(lambda x: x['grains'] >= 3, candidate_nodes=[])
as_list = list(more_grains)
assert as_list == []

some_or_no_grains = kb.filter(lambda x: x['grains'] >= -1, candidate_nodes=['tom', 'shamala'])
as_list = list(some_or_no_grains)
assert len(as_list) == 2
assert as_list[0] in ['tom', 'shamala']
assert as_list[1] in ['tom', 'shamala']
assert as_list[0] != as_list[1]

nodes = kb.filter(lambda x: True)
as_list = list(nodes)
assert len(as_list) == 3
jeraca = kb.node('jeraca')
assert len(jeraca.neighbors) == 0
shamala = kb.node('shamala')
assert len(shamala.neighbors) == 0
tom = kb.node('tom')
assert len(tom.neighbors) == 1
assert tom.neighbors[0][0] == 'shamala'
assert len(tom.neighbors[0][1]) == 1
assert tom.neighbors[0][1][0]['pred'] == 'knows'

fn_was_called = False
def watch_fn(node, prev_val):
    global fn_was_called
    fn_was_called = True
    assert prev_val == 0
    assert node.grains == 1
    assert len(node.neighbors) == 1
    assert kb.node(node.neighbors[0][0]) == 'shamala'

nights_watch = tom.watch('grains', watch_fn)
tom.grains += 1
assert fn_was_called
fn_was_called = False
tom.remove_watch(nights_watch)
tom.grains += 1
assert not fn_was_called
nights_watch = tom.watch('grains', watch_fn)
tom.remove_watch('grains')
tom.grains += 1
assert not fn_was_called

kb.store('node(i_am_node)', node_attributes=[{'foo': 'bar'}])
new_node = kb.node('i_am_node')
assert new_node.foo == 'bar'
new_node.foo = 'baz'
new_node = kb.node('i_am_node')
assert new_node.foo == 'baz'
kb.store('connected_nodes(3, 4)', node_attributes=[{'x': 3}, {'x': 4}], edge_attributes={'power_level': 3})
_3 = kb.node(3)
_4 = kb.node(4)
assert _3.x == 3
assert _4.x == 4
assert kb.edge(3, 'connected_nodes', 4).power_level == 3
kb.edge(3, 'connected_nodes', 4).power_level = 'high'
assert kb.edge(3, 'connected_nodes', 4).power_level == 'high'

print('All attribute tests passed.')