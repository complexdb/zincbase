import context

from zincbase import KB
kb = KB()

kb.store('bought_ticket(tom)')

rule_num = kb.store('winner(X) :- bought_ticket(X), had_correct_numbers(X)')

assert str(kb.rule('winner(X)')) == 'winner(X)'
assert kb.rule(rule_num) == kb.rule('winner(X)')

assert list(kb.query('winner(X)')) == []

fake_lottery_win = kb.store('had_correct_numbers(tom)')

assert list(kb.query('winner(X)')) == [{'X': 'tom'}]

kb.delete_rule(fake_lottery_win)

assert list(kb.query('winner(X)')) == []

tom = kb.node('tom')

def possible_winner(me, affected_nodes, node_that_changed, attr_changed, cur_val, prev_val):
    print('gooooo', me, affected_nodes, node_that_changed, attr_changed)
    pass

kb.rule(rule_num).on_change = possible_winner

def full_winner(node, prev_val):
    assert node.neighbors == []
    assert node.attrs == {'correct_numbers': 6}
    assert list(node.rules) == [] 
    if node.correct_numbers == 6:
        node.is_winner = True
        kb.store('had_correct_numbers(tom)')

kb.node('tom').watch('correct_numbers', full_winner)

kb.node('tom').correct_numbers = 6


print('Rules tests passed!')