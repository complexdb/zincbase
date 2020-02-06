from collections import defaultdict

import networkx as nx

class Node:
    """Class representing a node in the KB.
    """
    def __init__(self, kb, name, data, watches=[]):
        super().__setattr__('_kb', kb)
        super().__setattr__('_name', name)
        nx.set_node_attributes(self._kb.G, {self._name: data})
        self._watches = defaultdict(list)
        for watch in watches:
            self._watches[watch[0]].append(watch[1])
    
    def __repr__(self):
        return self._name
    
    def __eq__(self, comparator):
        return self._name == str(comparator)
    
    def __ne__(self, comparator):
        return self._name != str(comparator)

    def __getattr__(self, key):
        try:
            return self._kb.G.nodes(data=True)[self._name][key]
        except KeyError as e:
            return None

    def __setattr__(self, key, value):
        attrs = self._kb.G.nodes(data=True)[self._name]
        prev_val = attrs.get(key, None)
        attrs.update({key: value})
        nx.set_node_attributes(self._kb.G, {self._name: attrs})
        for watch_fn in self._watches.get(key, []):
            watch_fn(self, prev_val)

    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    
    @property
    def attrs(self):
        """Returns attributes of the node stored in the KB
        """
        attributes = self._kb.G.nodes(data=True)[self._name]
        try:
            del attributes['_watches']
            del attributes['_new_neighbor_fn']
        except:
            pass
        return attributes
    
    @property
    def neighbors(self):
        """Returns the node's neighbors, in the format of tuples:
        [(neighbor_name, [{'pred': predicate aka edge_relation}])]
        """
        return self._kb.neighbors(self._name)
    
    def watch(self, attribute, fn):
        """Execute user-defined function when the value of attribute changes.
        Function takes two args: `node` which has access to all
        its own attributes, including neighbors and edges, and the second
        arg is the previous value of the attribute that changed.

        :returns int: id of the watch

        :Example:

        >>> kb.store('node(node1)')
        >>> node = kb.node('node1')
        >>> node.grains = 3
        >>> print(node.grains)
        3
        >>> node.watch('grains', lambda x: print('grains changed to ' + x.grains))
        ('grains', 0)
        >>> node.grains += 1
        grains changed to 4

        """
        self._watches[attribute].append(fn)
        return (attribute, len(self._watches) - 1)
    
    def remove_watch(self, attribute_or_watch_id):
        """Stop watching `attribute_or_watch_id`.
        If it is a string, delete all watches for that attribute.
        If it is a tuple of (attribute, watch_id): delete that specific watch.
        """
        if isinstance(attribute_or_watch_id, tuple):
            self._watches[attribute_or_watch_id[0]].pop(attribute_or_watch_id[1])
        else:
            self._watches[attribute_or_watch_id] = []
    
    def watch_for_new_neighbor(self, fn):
        """Execute `fn` when node receives a new neighbor."""
        self.__setattr__('_new_neighbor_fn', fn)