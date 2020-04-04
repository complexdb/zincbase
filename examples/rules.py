from zincbase import KB

kb = KB()

kb.store('sku(tshirt)', node_attributes=[{'inventory': 10}])
kb.store('sku(jeans)', node_attributes=[{'inventory': 3}])
kb.store('top(tshirt)')
kb.store('bottom(jeans)')

rule_num = kb.store('outfit(X, Y) :- sku(X), sku(Y), top(X), bottom(Y)')
kb.rule(rule_num).inventory = min(kb.node('tshirt').inventory, kb.node('jeans').inventory)
print('starting with inventory', kb.rule(rule_num).inventory)

def inventory_changed(me, affected_nodes, node_that_changed, attr_changed, cur_val, prev_val):
    if prev_val is not None and cur_val > prev_val:
        print('YOU ORDERED MORE OF OUTFIT!!!', node_that_changed)
        for node in affected_nodes:
            print('ordering more of!', node)
            node.inventory += 1
    me.inventory = min([n.inventory for n in affected_nodes])
    if me.inventory is not None and me.inventory < 1:
        print('ordering a single more of', node_that_changed, node_that_changed.inventory)
        node_that_changed.inventory += 1
        print('after we ordered 1 more of :', node_that_changed, node_that_changed.inventory)
        print('we got this many outfits', kb.rule(rule_num).inventory)
    else:
        print('no need to order more!')

kb.rule(rule_num).on_change = inventory_changed
kb.node('jeans').inventory -= 1
print('our inventory of outfits is', kb.rule(rule_num).inventory)
kb.node('jeans').inventory -= 1
print('our inventory of outfits is', kb.rule(rule_num).inventory)
kb.node('jeans').inventory -= 1
print('our inventory of outfits is', kb.rule(rule_num).inventory)
kb.rule(rule_num).inventory += 1
print('this num should be 1 bigger than the last:', kb.rule(rule_num).inventory)
print('we got this jeans', kb.node('jeans').inventory)
print('we gonna sell 1 jeans')
kb.node('jeans').inventory -= 1
print('now we got this many jeans', kb.node('jeans').inventory)
print('after selling that, we got this many outfits', kb.rule(rule_num).inventory)

import sys; sys.exit(0)

def low_stock_sku(sku, prev_val):
    if sku.inventory > prev_val:
        return
    if 1 < sku.inventory < 5:
        print(f'Order more of {sku}!')
    elif sku.inventory < 1:
        print(f'Out of stock of {sku}!')

def sold_an_outfit(edge, prev_val):
    if prev_val < 1:
        raise Exception('unable to sell')
    for node in edge.nodes:
        node.inventory -= 1
    if edge.inventory < 1:
        out_of_stock_of = []
        for node in edge.nodes:
            if node.inventory < 1:
                out_of_stock_of.append(node)
        print(f'Unable to sell any more of {edge} because we ran out of {out_of_stock_of}!')
        for no_stock in out_of_stock_of:
            print(f'Will restock {no_stock}')
            kb.node(no_stock).restock(no_stock, 10)
            
def restock(sku, amount=1):
    node = kb.node(sku)
    sku.inventory += amount

kb.node('tshirt').watch('inventory', low_stock_sku)
kb.node('jeans').watch('inventory', low_stock_sku)
kb.node('tshirt').restock = restock
kb.node('jeans').restock = restock

kb.node('tshirt').inventory -= 6

kb.edge('tshirt', 'outfit', 'jeans').watch('inventory', sold_an_outfit)

kb.edge('tshirt', 'outfit', 'jeans').inventory -= 1
