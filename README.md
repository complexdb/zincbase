[![CircleCI](https://circleci.com/gh/complexdb/zincbase.svg?style=svg)](https://circleci.com/gh/complexdb/zincbase)
[![DOI](https://zenodo.org/badge/183831265.svg)](https://zenodo.org/badge/latestdoi/183831265)
[![Documentation Status](https://readthedocs.org/projects/zincbase/badge/?version=latest)](https://zincbase.readthedocs.io/en/latest/?badge=latest)
[![PyPI version fury.io](https://badge.fury.io/py/zincbase.svg)](https://pypi.python.org/pypi/zincbase/)
[![PyPI download month](https://img.shields.io/pypi/dm/zincbase.svg)](https://pypi.python.org/pypi/zincbase/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/zincbase.svg)](https://pypi.python.org/pypi/zincbase/)
[![PyPI license](https://img.shields.io/pypi/l/zincbase.svg)](https://pypi.python.org/pypi/zincbase/)

<img src="https://user-images.githubusercontent.com/2245347/57199440-c45daf00-6f33-11e9-91df-1a6a9cae6fb7.png" width="140" alt="Zincbase logo">

ZincBase is a state of the art knowledge base and complex simulation suite. It does the following:

* Store and retrieve graph structured data efficiently.
* Provide ways to query the graph, including via bleeding-edge graph neural networks.
* Simulate complex effects playing out across the graph and see how predictions change.

Zincbase exists to answer questions like "what is the probability that Tom likes LARPing", or "who likes LARPing", or "classify people into LARPers vs normies", or simulations like "what happens if all the LARPers become normies".

<img src="https://user-images.githubusercontent.com/2245347/57595488-2dc45b80-74fa-11e9-80f4-dc5c7a5b22de.png" width="320" alt="Example graph for reasoning">

It combines the latest in neural networks with symbolic logic (think expert systems and prolog), graph search, and complexity theory.

View full documentation [here](https://zincbase.readthedocs.io).

## Quickstart

`pip3 install zincbase`

```
from zincbase import KB
kb = KB()
kb.store('eats(tom, rice)')
for ans in kb.query('eats(tom, Food)'):
    print(ans['Food']) # prints 'rice'

...
# The included assets/countries_s1_train.csv contains triples like:
# (namibia, locatedin, africa)
# (lithuania, neighbor, poland)

kb = KB()
kb.from_csv('./assets/countries.csv')
kb.build_kg_model(cuda=False, embedding_size=40)
kb.train_kg_model(steps=2000, batch_size=1, verbose=False)
kb.estimate_triple_prob('fiji', 'locatedin', 'melanesia')
0.8467
```

# Requirements

* Python 3
* Libraries from requirements.txt
* GPU preferable for large graphs but not required

# Installation

`pip install -r requirements.txt`

_Note:_ Requirements might differ for PyTorch depending on your system.

# Testing

```
python test/test_main.py
python test/test_graph.py
... etc ... all the test files there
python -m doctest zincbase/zincbase.py
```

# Validation

"Countries" and "FB15k" datasets are included in this repo.

There is a script to evaluate that ZincBase gets at least as good
performance on the Countries dataset as the original (2019) RotatE paper. From the repo's
root directory:

```
python examples/eval_countries_s3.py
```

It tests the hardest Countries task and prints out the AUC ROC, which should be
~ 0.95 to match the paper. It takes about 30 minutes to run on a modern GPU.

There is also a script to evaluate performance on FB15k: `python examples/fb15k_mrr.py`.

## Building documentation

From docs/ dir: `make html`. If something changed a lot: `sphinx-apidoc -o . ..`

## Pushing to pypi

NOTE: This is now all automatic via CircleCI, but here are the manual steps for reference:

* Edit `setup.py` as appropriate (probably not necessary)
* Edit the version in `zincbase/__init__.py`
* From the top project directory `python setup.py sdist bdist_wheel --universal`
* `twine upload dist/*`

# TODO

* Refactor so edge is its own class
* Query all edges by attribute
* Rules (observables) to say 'on change of attribute, run this small program and propagate changes'
* * Will enable advanced simulation beginning with Abelian sandpile
* to_csv method
* To DOT, for visualization (integrate with github/anvaka/word2vec-graph)
* utilize postgres as backend triple store
* The to_csv/from_csv methods do not yet support node attributes.
* Reinforcement learning for graph traversal.

# References & Acknowledgements

[Theo Trouillon. Complex-Valued Embedding Models for Knowledge Graphs. Machine Learning[cs.LG]. Université Grenoble Alpes, 2017. English. ffNNT : 2017GREAM048](https://tel.archives-ouvertes.fr/tel-01692327/file/TROUILLON_2017_archivage.pdf)

[L334: Computational Syntax and Semantics -- Introduction to Prolog, Steve Harlow](http://www-users.york.ac.uk/~sjh1/courses/L334css/complete/complete2li1.html)

[Open Book Project: Prolog in Python, Chris Meyers](http://www.openbookproject.net/py4fun/prolog/intro.html)

[Prolog Interpreter in Javascript](https://curiosity-driven.org/prolog-interpreter)

[RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space, Zhiqing Sun and Zhi-Hong Deng and Jian-Yun Nie and Jian Tang, International Conference on Learning Representations, 2019](https://openreview.net/forum?id=HkgEQnRqYQ)

# Citing

If you use this software, please consider citing:

```
@software{zincbase,
  author = {{Tom Grek}},
  title = {ZincBase: A state of the art knowledge base},
  url = {https://github.com/tomgrek/zincbase},
  version = {0.1.1},
  date = {2019-05-12}
}

```

# Contributing

See CONTRIBUTING. And please do!