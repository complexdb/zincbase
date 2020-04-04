from zincbase.utils.string_utils import split_on

from zincbase.logic.Term import Term

class Rule(dict):
    
    def __init__(self, expr, on_change=None, kb=None):
        parts = split_on(expr, ':-')
        self.head = Term(parts[0], kb=kb)
        self.goals = []
        self._kb = kb
        self.on_change = on_change
        self._locked = False
        if len(parts) == 2:
            sub_goals = split_on(parts[1], ',')
            for sub_goal in sub_goals:
                self.goals.append(Term(sub_goal, kb=self._kb))
    
    def __repr__(self):
        return str(self.head)
    
    def execute_change(self, changed_node, attribute, new_value, prev_val):
        """Function to execute when any node that's part of this
        rule gets changed.

        :param changed_node: The node that changed
        :param attribute: The attribute of the node that changed
        :param new_value: The new value of the changed attribute
        :param prev_val: The previous value of the changed attribute
        """
        if not self.on_change or self._locked:
            return False
        self._locked = True
        self.on_change(self, self.affected_nodes, changed_node, attribute, new_value, prev_val)
        self._locked = False
    
    @property
    def affected_nodes(self):
        bindings = list(self._kb.query(str(self)))
        if not bindings:
            return []
        else:
            return [self._kb.node(x) for x in bindings[0].values()]
        return bindings

    def __getattr__(self, key):
        try:
            return self[key]
        except:
            raise AttributeError
    
    def __setattr__(self, key, value):
        if key not in ('_kb', 'head', 'goals', 'on_change', '_locked'):
            try:
                prev_val = self.__dict__[key]
            except:
                prev_val = None
            if self.on_change and prev_val is not None:
                if not self._locked:
                    with self._kb.dont_propagate():
                        self._locked = True
                        self.on_change(self, self.affected_nodes, self, key, value, prev_val)
                self._locked = False
        super().__setattr__(key, value)