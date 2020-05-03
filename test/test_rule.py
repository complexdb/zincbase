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
assert 'tom' in kb._node_cache
del tom
assert 'tom' not in kb._node_cache

possible_winner_called = 0
def possible_winner(me, affected_nodes, node_that_changed, attr_changed, cur_val, prev_val):
    global possible_winner_called
    if cur_val != 6:
        possible_winner_called += 1
        return False
kb.rule(rule_num).on_change = possible_winner

# full_winner() below is called when the correct_numbers property on node is changed
# We can't then, inside that fn, set node.is_winner without increasing the recursion
# limit (we're already inside of a recursion)
kb.set_recursion_limit(2)

full_winner_called = 0
def full_winner(node, prev_val):
    global full_winner_called
    if node.correct_numbers != 6:
        return False
    assert node.neighbors == []
    assert node.attrs == {'correct_numbers': 6}
    if node.correct_numbers == 6:
        with kb.dont_propagate():
            node.is_winner = True
        assert node.is_winner
        kb.store(f'had_correct_numbers({str(node)})')
        full_winner_called += 1

kb.node('tom').watch('correct_numbers', full_winner)
kb.node('tom').correct_numbers = 5
assert possible_winner_called == 1
assert kb.node('tom').correct_numbers == 5
kb.node('tom').correct_numbers = 6
assert kb.node('tom').correct_numbers == 6
assert kb.node('tom').is_winner
assert possible_winner_called == 1
assert full_winner_called == 1

possible_winner_called = 0
full_winner_called = 0
kb.store('bought_ticket(shamala)')
shamala = kb.node('shamala')
assert 'shamala' in kb._node_cache
shamala.watch('correct_numbers', full_winner)
shamala.correct_numbers = 5
assert possible_winner_called == 1
assert shamala.correct_numbers == 5
shamala.correct_numbers = 6
assert shamala.correct_numbers == 6
assert shamala.is_winner
assert possible_winner_called == 1
assert full_winner_called == 1

print('Rules tests passed!')