import networkx as nx

# it should also have a .neighbors prop

class Node:

    def __init__(self, G, name, data):
        super().__setattr__('_G', G)
        super().__setattr__('_name', name)
        nx.set_node_attributes(self._G, {self._name: data})
    
    def __repr__(self):
        return self._name
    
    def __eq__(self, comparator):
        return self._name == str(comparator)
    
    def __ne__(self, comparator):
        return self._name != str(comparator)

    def __getattr__(self, key):
        try:
            return self._G.nodes(data=True)[self._name][key]
        except KeyError as e:
            return None

    def __setattr__(self, key, value):
        attrs = self._G.nodes(data=True)[self._name]
        attrs.update({key: value})
        nx.set_node_attributes(self._G, {self._name: attrs})

    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __setitem__(self, key, value):
        return self.__setattr__(key, value)
    
    @property
    def attrs(self):
        return self._G.nodes(data=True)[self._name]