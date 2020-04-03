import copy
from zincbase import KB
kb = KB()
from zincbase.logic.Rule import Rule
kb.store('tshirt(hello)')
qwe = Rule('outfit(X):-tshirt(X)', kb=kb)
kb.node('hello').zig = 1
copy.deepcopy(qwe)