"""This file simulates the famous Conway's Game of Life cellular automata.
There's no pressing need to do this using Zincbase -- it's just a demo.
"""

import random
import time

from zincbase import KB
from zincbase.web import GraphCaster

kb = KB()
g = GraphCaster()
g.reset()

kb.store('node(1)', node_attributes=[{'color': 0x00ff00}])
kb.store('node(2)', node_attributes=[{'color': 0x0000ff}])
kb.store('node(3)', node_attributes=[{'color': 0xff00ff}])
kb.store('node(4)', node_attributes=[{'color': 0xffee11}])
kb.store('edge(1, 2)', edge_attributes={'edge_attr': 1})
kb.store('edge(2, 3)', edge_attributes={'edge_attr': 2})
kb.store('edge(2, 4)', edge_attributes={'edge_attr': 3})

g.from_kb(kb)
g.render(node_color='node => node.color',
         arrow_size=2,
         node_opacity=1, node_label='color',
         label_node=True,
         edge_label='edge_attr',
         label_edge=True, label_edge_offset=1,
         bg_color='rgba(255,255,255,1)')

while True:
    time.sleep(1)
    node_to_update = kb.node(random.choice([1,2,3,4]))
    node_to_update.color=random.randint(0, 0xffffff)
    g.update_node(node_to_update, defer=True)
    from_node = random.choice([1,2])
    to_node = random.choice([2,3,4])
    if from_node == 1 and to_node != 2:
        pass
    elif from_node == to_node:
        pass
    else:
        from_node = str(from_node); to_node = str(to_node)
        kb.edge_attr(from_node, 'edge', to_node, {'edge_attr': random.randint(0, 100)})
        g.update_edge(from_node, 'edge', to_node, kb, defer=True)
    g.batch_update()