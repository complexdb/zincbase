from collections import defaultdict
import copy

import networkx as nx

class Edge:
    """Class representing an edge in the KB.
    """
    def __init__(self, kb, sub, pred, ob, data={}, watches=[]):
        super().__setattr__('_kb', kb)
        super().__setattr__('_name', str(sub) + '___' + str(pred) + '___' + str(ob))
        super().__setattr__('_sub', str(sub))
        super().__setattr__('_pred', str(pred))
        super().__setattr__('_ob', str(ob))
        super().__setattr__('_recursion_depth', 0)
        super().__setattr__('_watches', defaultdict(list))
        super().__setattr__('_edge', self._kb.G[self._sub][self._ob])
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
            for _, edge in self._edge.items():
                if edge['pred'] == self._pred:
                    return edge[key]
        except KeyError as e:
            return None

    def __setattr__(self, key, value):
        if self._kb._global_propagations > self._kb._PROPAGATION_LIMIT:
            return False
        if self._recursion_depth > self._kb._MAX_RECURSION:
            return False
        self._kb._global_propagations += 1
        super().__setattr__('_recursion_depth', self._recursion_depth + 1)
        for _, attrs in self._edge.items():
            if attrs['pred'] == self._pred:
                prev_val = attrs.get(key, None)
                attrs.update({key: value})
                if not self._kb._dont_propagate:
                    for watch_fn in self._watches.get(key, []):
                        watch_fn(self, prev_val)
                super().__setattr__('_recursion_depth', self._recursion_depth - 1)
                self._kb._global_propagations -= 1

    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    
    def __delitem__(self, attr):
        for _, attrs in self._edge.items():
            if attrs['pred'] == self._pred:
                del attrs[attr]
    
    def get(self, attr, default):
        try:
            return self.attrs[attr]
        except:
            return default

    @property
    def nodes(self):
        """Return the nodes that this edge is connected to as tuple of (subject, object)
        """
        return [self._kb.node(self._sub), self._kb.node(self._ob)]

    @property
    def attrs(self):
        """Returns attributes of the edge stored in the KB
        """
        attributes = None
        for _, edge in self._edge.items():
            if edge['pred'] == self._pred:
                attributes = copy.deepcopy(edge)
        if attributes is None:
            return False
        try:
            del attributes['pred']
            del attributes['_watches']
        except:
            pass
        return attributes
    
    def watch(self, attribute, fn):
        """Execute user-defined function when the value of attribute changes.
        Function takes two args: `edge` which has access to all
        its own attributes, and the second
        arg is the previous value of the attribute that changed.

        As cycles are possible in the graph, changes to an edge attribute, that
        change the attributes of the nodes it's connected to, etc,
        may eventually propagate back to change the original edge's attribute again,
        ad infinitum until the stack explodes. To prevent this, in one "update cycle", more
        than `kb._MAX_RECURSION` updates will be rejected.

        :returns int: id of the watch

        :Example:

        >>> from zincbase import KB
        >>> kb = KB()
        >>> kb.store('edge(a,b)')
        0
        >>> edge = kb.edge('a', 'edge', 'b')
        >>> edge.resistance = 3
        >>> print(edge.resistance)
        3
        >>> edge.watch('resistance', lambda x, prev_val: print('resistance changed to ' + str(x.resistance)))
        ('resistance', 0)
        >>> edge.resistance += 1
        resistance changed to 4

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