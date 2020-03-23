"""This file simulates the famous Conway's Game of Life cellular automata
just as in the basic example, but this does 3D WebGL.
There's no pressing need to do this using Zincbase -- it's just a demo.
Usage: run `python -m zincbase.web` & `python gol.py`
Open your web browser to localhost:5000

"""

import random

import cv2
import numpy as np
from PIL import Image
import torch

from zincbase import KB
from zincbase.web import GraphCaster

MAX_Y = 30
MAX_X = 30

kb = KB()
g = GraphCaster()
g.reset()

for y in range(MAX_Y):
    for x in range(MAX_X):
        state = torch.bernoulli(torch.tensor([0.4])).int().item()
        node_id = (y * MAX_X) + x
        kb.store(f'cell({node_id})', node_attributes=[{'state': state}])

for y in range(MAX_Y):
    for x in range(MAX_X):
        neighbors = ((-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 1),
                     (1, -1), (1, 0), (1, 1))
        for neighbor in neighbors:
            y_n = y + neighbor[0]
            x_n = x + neighbor[1]
            if y_n >= 0 and x_n >= 0 and y_n < MAX_Y and x_n < MAX_X:
                from_node = (y * MAX_X) + x
                to_node = (y_n * MAX_X) + x_n
                kb.store(f'neighbors({from_node}, {to_node})')

def graph_to_array():
    arr = []
    for y in range(MAX_Y):
        for x in range(MAX_X):
            arr.append(kb.node((y * MAX_X) + x).state)
    return arr

cv2.namedWindow("gol", cv2.WINDOW_NORMAL)
g.from_kb(kb)
g.render(node_color='node => node.state * 100000',
         node_size='node => (node.state + 1) * 10',
         node_opacity=0.7, node_label='node => node.id',
         edge_visibility=False,
         bg_color='rgba(255,255,255,1)')

import time; time.sleep(15)

while True:
    arr = graph_to_array()
    arr = torch.tensor(arr).view(MAX_Y, MAX_X)
    arr = np.int8(arr) * 255
    img = Image.fromarray(arr).convert('RGB')
    img = np.array(img)
    cv2.imshow("gol", img)
    q = cv2.waitKey(1)
    if q == 113: # 'q'
        cv2.destroyAllWindows()
        import sys; sys.exit(0)
    with kb.dont_propagate():
        for node in range(MAX_Y*MAX_X):
            n = kb.node(node)
            live_neighbors = sum([1 if kb.node(nn[0]).state else 0 for nn in n.neighbors])
            if n.state == 1:
                if live_neighbors not in (2, 3):
                    n.next_state = 0
                else:
                    n.next_state = n.state
            else:
                if live_neighbors == 3:
                    n.next_state = 1
                else:
                    n.next_state = n.state
        for node in range(MAX_Y*MAX_X):
            n = kb.node(node)
            n.state = n.next_state
            g.update_node(n, defer=True)
            n.next_state = None
    g.batch_update()