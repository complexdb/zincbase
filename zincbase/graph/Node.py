from collections import defaultdict
import copy

import networkx as nx

class Node:
    """Class representing a node in the KB.
    """
    def __init__(self, kb, name, data, watches=[]):
        super().__setattr__('_kb', kb)
        super().__setattr__('_name', name)
        super().__setattr__('_recursion_depth', 0)
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
    
    def __iter__(self):
        for attr in self.attrs:
            yield(attr)

    def __getattr__(self, key):
        try:
            return self._kb.G.nodes(data=True)[self._name][key]
        except KeyError as e:
            return None

    def __setattr__(self, key, value):
        if self._kb._global_propagations > self._kb._PROPAGATION_LIMIT:
            return False
        if self._recursion_depth > self._kb._MAX_RECURSION:
            return False
        self._kb._global_propagations += 1
        super().__setattr__('_recursion_depth', self._recursion_depth + 1)
        attrs = self._kb.G.nodes(data=True)[self._name]
        prev_val = attrs.get(key, None)
        attrs.update({key: value})
        nx.set_node_attributes(self._kb.G, {self._name: attrs})
        if not self._kb._dont_propagate:
            for watch_fn in self._watches.get(key, []):
                watch_fn(self, prev_val)
        super().__setattr__('_recursion_depth', self._recursion_depth - 1)
        self._kb._global_propagations -= 1

    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    
    def __delitem__(self, key):
        del self._kb.G.nodes[self._name][key]
    
    @property
    def attrs(self):
        """Returns attributes of the node stored in the KB
        """
        attributes = self._kb.G.nodes(data=True)[self._name]
        attributes = copy.deepcopy(attributes)
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

        As cycles are possible in the graph, changes to a node attribute, that
        change its neighbors attributes etc, may eventually propagate back
        to change the original node's attribute again, ad infinitum until
        the stack explodes. To prevent this, in one "update cycle", more
        than `kb._MAX_RECURSION` updates will be rejected.

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