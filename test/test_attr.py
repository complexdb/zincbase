import context

from zincbase import KB

kb = KB()
kb.seed(555)

kb.store('person(tom)')
kb.store('person(shamala)')
kb.store('knows(tom, shamala)')
assert kb.neighbors('tom') == [('shamala', [{'pred': 'knows'}])]

kb.attr('tom', { 'grains': 0 })
kb.attr('shamala', { 'grains': 5 })
kb.store('person(jeraca)')
kb.attr('jeraca', { 'grains': 3 })

zero_grains = list(kb.filter(lambda x: x['grains'] == 0))
assert len(zero_grains) == 1
assert zero_grains[0] == 'tom'

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

print('All attribute tests passed.')