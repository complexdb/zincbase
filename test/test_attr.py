import context

from zincbase import KB

kb = KB()
kb.seed(555)

kb.store('person(tom)')
kb.store('person(shamala)')
kb.store('knows(tom, shamala)')
assert kb.neighbors('tom') == [('shamala', [{'pred': 'knows'}])]

kb.attr('tom', { 'grains': 0 })

print('All attribute tests passed.')