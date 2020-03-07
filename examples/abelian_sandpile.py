"""Simulate an Abelian sandpile. See how the end state (which is pretty, as
complex self-organizing things tend to be) is the same, regardless that some
random choices are made along the way.

Usage: `python3 abelian_sandpile.py [recursion_limit] [propagation_limit]`

The defaults are 15 for both recursion and propagation. You'll see sandpiles of
~15 grains fall at once. It's (much) slower than if you increase the limits;
but increase too much and Python/your computer might not like it. Alternatively,
set the values low like `1 1` if you prefer to watch the pretty animation.

On a reasonable computer, limits of 100000 work ok, but if you change the grid
size (MAX_Y & MAX_X in the code below), that's probably going to be too much.
"""

import random
import sys
import textwrap
import time

import cv2
import numpy as np
from PIL import Image
import torch

from zincbase import KB

kb = KB()

MAX_Y = 100
MAX_X = 100

try:
    recursion_limit = int(sys.argv[1])
except IndexError:
    print(textwrap.dedent("""\nSetting recursion limit to 15. This is cautious and slow. \
Specify a first arg to change it, e.g. `python3 abelian_sandpile.py 10000 5000`"""))
    recursion_limit = 15
try:
    propagation_limit = int(sys.argv[2])
except IndexError:
    print(textwrap.dedent("""\nSetting propagation limit to 15. You'll see blobs of sand change \
~15 cells at a time. This is cautious and slow. \
Specify a second arg to change it, e.g. `python3 abelian_sandpile.py 10000 5000`\n"""))
    propagation_limit = 15

kb.set_recursion_limit(recursion_limit)
kb.set_propagation_limit(propagation_limit)

def evolve(toppler, prev_val):
    if kb.node(toppler).grains < 4:
        return False
    toppler.grains -= 4
    for n, pred in toppler.neighbors:
        n = kb.node(n)
        n.grains += 1

for y in range(MAX_Y):
    for x in range(MAX_X):
        kb.store(f'cell({(y * MAX_Y) + x})', node_attributes=[{'x': x, 'y': y, 'grains': 0}])
        node = kb.node((y * MAX_Y) + x)
        node.watch('grains', evolve)

for y in range(MAX_Y):
    for x in range(MAX_X):
        neighbors = ((-1, 0), (0, -1), (0, 1), (1, 0))
        for neighbor in neighbors:
            y_n = y + neighbor[0]
            x_n = x + neighbor[1]
            if y_n >= 0 and x_n >= 0 and y_n < MAX_Y and x_n < MAX_X:
                kb.store(f'neighbors({(y * MAX_Y) + x}, {(y_n * MAX_Y) + x_n})')
            else:
                kb.node((y * MAX_Y) + x).is_edge = True

def graph_to_array():
    arr_b, arr_g, arr_r = [], [], []
    for y in range(MAX_Y):
        for x in range(MAX_X):
            val = min(kb.node((y * MAX_Y) + x).grains, 255)
            if val > 3:
                arr_r.append(max(100, val))
                arr_g.append(max(100, val))
                arr_b.append(max(100, val))
            elif val == 3:
                arr_r.append(255)
                arr_g.append(0)
                arr_b.append(0)
            elif val == 2:
                arr_r.append(0)
                arr_g.append(200)
                arr_b.append(255)
            elif val == 1:
                arr_r.append(0)
                arr_g.append(255)
                arr_b.append(0)
            else:
                arr_r.append(0)
                arr_g.append(0)
                arr_b.append(0)
    return arr_b, arr_g, arr_r

frame_time = 0
cv2.namedWindow("gol", cv2.WINDOW_NORMAL)

central_node = (MAX_Y * MAX_X) // 2 + MAX_X // 2
central_node = kb.node(central_node)

start_time = time.time()

central_node.grains += 3000

import gc
gc.disable()

while True:
    arr_b, arr_g, arr_r = graph_to_array()
    arr = np.uint8(arr_b).reshape(MAX_Y, MAX_X, 1)
    arrg = np.uint8(arr_g).reshape(MAX_Y, MAX_X, 1)
    arrr = np.uint8(arr_r).reshape(MAX_Y, MAX_X, 1)
    arr = np.concatenate((arr, arrg), axis=-1)
    arr = np.concatenate((arr, arrr), axis=-1)
    img = Image.fromarray(arr)
    img = np.array(img)
    cv2.imshow("gol", img)
    q = cv2.waitKey(1)
    if q == 113: # 'q'
        cv2.destroyAllWindows()
        import sys; sys.exit(0)
    unstable_nodes = list(kb.filter(lambda x: x.grains > 3))
    # filter_fast can be up to ~2.5x faster than version above,
    # depending on the size of the grid. Here's the alternative:
    # unstable_nodes = list(kb.filter_fast(lambda x: x[:, 0] > 3, attributes=['grains']))
    try:
        toppler = random.choice(unstable_nodes)
    except IndexError:
        # no unstable nodes.
        print(time.time() - start_time)
        # wait for user. Type q to exit.
        import pdb; pdb.set_trace()
    
    evolve(toppler, 0)
    