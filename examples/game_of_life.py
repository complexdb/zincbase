"""This file simulates the famous Conway's Game of Life cellular automata.
There's no pressing need to do this using Zincbase -- it's just a demo.
"""

import random

import cv2
import numpy as np
from PIL import Image
import torch

from zincbase import KB

MAX_Y = 100
MAX_X = 100

kb = KB()      

for y in range(MAX_Y):
    for x in range(MAX_X):
        state = torch.bernoulli(torch.tensor([0.4])).int().item()
        kb.store(f'cell({(y * MAX_X) + x})', node_attributes=[{'x': x, 'y': y, 'state': state}])
        node = kb.node((y * MAX_X) + x)

for y in range(MAX_Y):
    for x in range(MAX_X):
        neighbors = ((-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 1),
                     (1, -1), (1, 0), (1, 1))
        for neighbor in neighbors:
            y_n = y + neighbor[0]
            x_n = x + neighbor[1]
            if y_n >= 0 and x_n >= 0 and y_n < MAX_Y and x_n < MAX_X:
                kb.store(f'neighbors({(y * MAX_X) + x}, {(y_n * MAX_X) + x_n})')

def graph_to_array():
    arr = []
    for y in range(MAX_Y):
        for x in range(MAX_X):
            arr.append(kb.node((y * MAX_X) + x).state)
    return arr

cv2.namedWindow("gol", cv2.WINDOW_NORMAL)

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
            n.next_state = None