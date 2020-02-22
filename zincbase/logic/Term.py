"""A base unit for ZincBase's Prolog-like implementation of 'facts'"""

from zincbase.utils.string_utils import split_on

class Term:
    def __init__(self, expr, args=None, kb=None):
        if args:
            self.pred = expr
            self.args = args
        elif expr[-1] == ']':
            arr = split_on(expr[1:-1], ',')
            headtail = split_on(expr[1:-1], '|')
            if len(headtail) > 1:
                self.args = [Term(f, kb=kb) for f in headtail]
                self.pred = '__list__'
            else:
                arr.reverse()
                first = Term('__list__', [])
                for part in arr:
                    first = Term('__list__', [Term(part, kb=kb), first], kb=kb)
                self.pred = first.pred
                self.args = first.args
        elif expr[-1] == ')':
            sub_exprs = split_on(expr, '(', all=False)
            if len(sub_exprs) != 2:
                raise Exception('Syntax error')
            self.args = [Term(sub_expr, kb=kb) for sub_expr in split_on(sub_exprs[1][:-1], ',')]
            self.pred = sub_exprs[0]
        else:
            self.pred = expr
            self.args = []

        if kb is not None:
            for i, arg in enumerate(self.args):
                if arg:
                    added_node_1 = False
                    if not kb.G.has_node(str(arg)):
                        kb.G.add_node(str(arg))
                        added_node_1 = True
                    for arg2 in self.args[i+1:]:
                        added_node_2 = False
                        if not kb.G.has_node(str(arg2)):
                            kb.G.add_node(str(arg2))
                            added_node_2 = True
                        kb.G.add_edge(str(arg), str(arg2), pred=self.pred)
                        if added_node_1:
                            node = kb.node(str(arg2))
                            try:
                                if not kb._dont_propagate:
                                    node._new_neighbor_fn(str(arg))
                            except Exception as e:
                                pass
                        if added_node_2:
                            node = kb.node(str(arg))
                            try:
                                if not kb._dont_propagate:
                                    node._new_neighbor_fn(str(arg2))
                            except Exception as e:
                                pass


    def __repr__(self):
        if self.pred == '__list__':
            if not self.args:
                return '[]'
            first = self.args[1]
            if first.pred == '__list__' and first.args == []:
                return '[{}]'.format(str(self.args[0]))
            elif first.pred == '__list__':
                return '[{},{}]'.format(str(self.args[0]), str(self.args[1])[1:-1])
            else:
                return '[{}|{}]'.format(str(self.args[0]), str(self.args[1]))
        elif self.args:
            return '{}({})'.format(self.pred, ', '.join(map(str,self.args)))
        else:
            return self.pred
