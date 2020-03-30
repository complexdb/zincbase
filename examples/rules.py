from zincbase import KB

kb = KB()

kb.store('sku(tshirt)', node_attributes=[{'inventory': 10}])
kb.store('sku(jeans)', node_attributes=[{'inventory': 1}])
kb.store('top(tshirt)')
#kb.store('outfit(tshirt, jeans)', edge_attributes={'inventory': min(kb.node('tshirt').inventory, kb.node('jeans').inventory)})

kb.store('outfit(X,Y) :- sku(X), sku(Y), top(X)')
print('boop', list(kb.query('outfit(X,Y)')))

import ipdb; ipdb.set_trace()

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
