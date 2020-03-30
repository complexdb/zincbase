from zincbase.utils.string_utils import split_on

from zincbase.logic.Term import Term

class Rule:
    
    def __init__(self, expr, kb=None):
        parts = split_on(expr, ':-')
        self.head = Term(parts[0], kb=kb)
        self.goals = []
        if len(parts) == 2:
            sub_goals = split_on(parts[1], ',')
            for sub_goal in sub_goals:
                self.goals.append(Term(sub_goal, kb=kb))
    
    def __repr__(self):
        return str(self.head)
    
    def on_change(self, changed_node, prev_val):
        print("buggetty boo", self, prev_val)
        next if self.head.kb is not none, we can do 
        self.head.kb.query ... maybe
        how to get from here to triggering "stock low" alert
        when one of our inventory node attributes changes??
        probably not too hard.