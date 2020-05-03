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
# tom = kb.node('tom')
# del tom
possible_winner_called = 0
def possible_winner(me, affected_nodes, node_that_changed, attr_changed, cur_val, prev_val):
    global possible_winner_called
    if cur_val != 6:
        possible_winner_called += 1
        return False
kb.rule(rule_num).on_change = possible_winner

full_winner_called = 0
def full_winner(node, prev_val):
    global full_winner_called
    print('we woz called', node, prev_val)
    if node.correct_numbers != 6:
        return False
    assert node.neighbors == []
    assert node.attrs == {'correct_numbers': 6}
    if node.correct_numbers == 6:
        node.is_winner = True
        kb.store(f'had_correct_numbers({str(node)})')
        full_winner_called += 1

kb.node('tom').watch('correct_numbers', full_winner)
kb.node('tom').correct_numbers = 5
assert possible_winner_called == 1
assert kb.node('tom').correct_numbers == 5

kb.node('tom').correct_numbers = 6
assert kb.node('tom').correct_numbers == 6
assert possible_winner_called == 1
import ipdb; ipdb.set_trace()
TODO next is the Node class is entirely in-memory still. Need to factor
it out as a serde redis object, just as successfully done with Rule. It works
with {} as the node_cache but not with weakref.

#assert full_winner_called == 1


print('Rules tests passed!')