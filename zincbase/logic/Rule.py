from zincbase.utils.string_utils import split_on

from zincbase.logic.Term import Term

class Rule:
    
    def __init__(self, expr, on_change=None, kb=None):
        print('making new rule')
        parts = split_on(expr, ':-')
        self.head = Term(parts[0], kb=kb)
        self.goals = []
        self._kb = kb
        self.on_change = on_change
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
        print('executing a change!')
        if not self.on_change:
            return False
        self.on_change(self.affected_nodes, changed_node, attribute, new_value, prev_val)

        # next if self.head.kb is not none, we can do 
        # self.head.kb.query ... maybe
        # how to get from here to triggering "stock low" alert
        # when one of our inventory node attributes changes??
        # probably not too hard.
    
    @property
    def affected_nodes(self):
        print('QUERYING ON!!!', str(self))
        #import ipdb; ipdb.set_trace()
        bindings = self._kb.query(str(self))
        return bindings