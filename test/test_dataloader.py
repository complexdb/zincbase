from zincbase import KB
from zincbase.nn.dataloader import RedisGraph

kb = KB('localhost', 6379, 2)
kb.reset()
for l in ['a','b','c']:
    for l2 in ['d','e','f']:
        kb.store(f'links({l}, {l2})')
kb.store('~links(a,c)')
qwe = RedisGraph(kb, mode='head-batch')
as_list = [x for x in qwe]
assert len(as_list) == 10
kb.build_kg_model()
kb.train_kg_model(steps=100)
assert kb.estimate_triple_prob('a','links','d') > 0.9
assert kb.estimate_triple_prob('b','links','c') < 0.1
assert kb.estimate_triple_prob('c','links','f') > 0.9

print("All data loader tests passed.")