from collections import defaultdict
import copy

import dill
import networkx as nx

from zincbase import context

class Edge:
    """Class representing an edge in the KB.
    """
    def __init__(self, sub, pred, ob, data={}, watches=[]):
        super().__setattr__('_name', str(sub) + '__' + str(pred) + '__' + str(ob))
        super().__setattr__('_sub', str(sub))
        super().__setattr__('_pred', str(pred))
        super().__setattr__('_ob', str(ob))
        super().__setattr__('_recursion_depth', 0)
        data.update({'_watches': defaultdict(list)})
        for watch in watches:
            data['_watches'][watch[0]].append(watch[1])
        super().__setattr__('_dict', data)
    
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
            if key in ('__getstate__', '__deepcopy__', '__setstate__'):
                raise AttributeError
            if key == 'pred':
                return self._pred
            return self._dict.get(key, None)
        except KeyError as e:
            return None

    def __setattr__(self, key, value):
        if context.kb._global_propagations > context.kb._PROPAGATION_LIMIT:
            return False
        if self._recursion_depth > context.kb._MAX_RECURSION:
            return False
        context.kb._global_propagations += 1
        super().__setattr__('_recursion_depth', self._recursion_depth + 1)
        prev_val = self._dict.get(key, None)
        self._dict.update({key: value})
        me = dill.dumps(self)
        context.kb.redis.set(self._name + '__edge', me)
        if not context.kb._dont_propagate:
            for watch_fn in self._dict['_watches'].get(key, []):
                watch_fn(self, prev_val)
        super().__setattr__('_recursion_depth', self._recursion_depth - 1)
        me = dill.dumps(self)
        context.kb.redis.set(self._name + '__edge', me)
        context.kb._global_propagations -= 1

    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    
    def __delitem__(self, attr):
        del self._dict[attr]
        me = dill.dumps(self)
        context.kb.redis.set(self._name + '__edge', me)
    
    def get(self, attr, default):
        try:
            return self.attrs[attr]
        except:
            return default

    @property
    def nodes(self):
        """Return the nodes that this edge is connected to as tuple of (subject, object)
        """
        return [context.kb.node(self._sub), context.kb.node(self._ob)]

    @property
    def attrs(self):
        """Returns attributes of the edge stored in the KB
        """
        attributes = self._dict
        attributes = copy.deepcopy(attributes)
        try:
            del attributes['_watches']
            del attributes['pred']
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
        with context.kb.dont_propagate():
            self._dict['_watches'][attribute].append(fn)
            me = dill.dumps(self)
            context.kb.redis.set(self._name + '__edge', me)
        return (attribute, len(self._dict['_watches']) - 1)
    
    def remove_watch(self, attribute_or_watch_id):
        """Stop watching `attribute_or_watch_id`.
        If it is a string, delete all watches for that attribute.
        If it is a tuple of (attribute, watch_id): delete that specific watch.
        """
        if isinstance(attribute_or_watch_id, tuple):
            self._dict['_watches'][attribute_or_watch_id[0]].pop(attribute_or_watch_id[1])
        else:
            self._dict['_watches'][attribute_or_watch_id] = []
        me = dill.dumps(self)
        context.kb.redis.set(self._name + '__edge', me)