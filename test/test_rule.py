import context

from zincbase import KB
kb = KB('localhost', '6379', 2)
kb.reset()

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

possible_winner_called = 0
def possible_winner(me, affected_nodes, node_that_changed, attr_changed, cur_val, prev_val):
    global possible_winner_called
    print('was called!!!!!!!!!!!!')
    if cur_val != 6:
        possible_winner_called += 1
        return False
kb.rule(rule_num).on_change = possible_winner
print(f'This should exist: {kb.rule(rule_num).on_change}')
# TODO Next what I am trying to do here is to
# update the rule as stored in redis when there's
# an update, e.g., an on_change function (or anything
# in the rule's __setattr__)

full_winner_called = 0
def full_winner(node, prev_val):
    global full_winner_called
    if node.correct_numbers != 6:
        return False
    assert node.neighbors == []
    assert node.attrs == {'correct_numbers': 6}
    if node.correct_numbers == 6:
        node.is_winner = True
        kb.store(f'had_correct_numbers({str(node)})')
        full_winner_called += 1

kb.node('tom').watch('correct_numbers', full_winner)
import ipdb; ipdb.set_trace()
kb.node('tom').correct_numbers = 5
assert possible_winner_called == 1
kb.node('tom').correct_numbers = 6
assert possible_winner_called == 2
assert full_winner_called == 1


print('Rules tests passed!')