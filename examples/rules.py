from zincbase import KB

kb = KB()

kb.store('sku(tshirt)', node_attributes=[{'inventory': 10}])
kb.store('sku(jeans)', node_attributes=[{'inventory': 1}])
kb.store('top(tshirt)')
#kb.store('outfit(tshirt, jeans)', edge_attributes={'inventory': min(kb.node('tshirt').inventory, kb.node('jeans').inventory)})

kb.store('outfit(X,Y) :- sku(X), sku(Y), top(X)')
#print('boop', list(kb.query('outfit(X,Y)')))
def mee(other_affected_nodes, node_that_changed, attr_changed, cur_val, prev_val):
    #import ipdb; ipdb.set_trace()
    affected_nodes = list(other_affected_nodes)
    print("foo!", affected_nodes, node_that_changed, attr_changed, cur_val, prev_val)
kb.rule(3).on_change = mee
kb.node('tshirt').zig = 1
#import ipdb; ipdb.set_trace()
NEXT must get affected nodes to work. That way, when the outfit.on_change is called,
we can see not only that tshirt stock dropped too low and we must call tshirt's watch
in order to order more --- but we can also check on the stock for other affected
nodes (e.g. if X=tshirt, other affected nodes would be jeans) and maybe order the same
amount of extra jeans as we're about to order of tshirts.

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
