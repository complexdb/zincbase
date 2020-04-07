# Example: Using Zincbase to create a Rules Engine
# Our clothing shop is going to run itself.

from zincbase import KB

kb = KB()

# Our shop sells 2 SKUs, a tshirt, and jeans. Each has some stock.

kb.store('sku(tshirt)', node_attributes=[{'inventory': 10}])
kb.store('sku(jeans)', node_attributes=[{'inventory': 3}])

# Customers can buy them individually or as an outfit.

kb.store('top(tshirt)')
kb.store('bottom(jeans)')
rule_num = kb.store('outfit(X, Y) :- sku(X), sku(Y), top(X), bottom(Y)')

# grab the stored nodes and rule for later use

tshirt = kb.node('tshirt')
jeans = kb.node('jeans')
outfit = kb.rule(rule_num)

# Set the initial stock level of outfits

outfit.inventory = min(tshirt.inventory, jeans.inventory)

# Print our initial stock levels
def print_stock():
    print("--- stock take ---")
    print(f"T-Shirts: {tshirt.inventory}")
    print(f"Jeans: {jeans.inventory}")
    print(f"Complete outfits we can sell: {outfit.inventory}")
    print("--- stock take complete ---\n")

print("To begin with, here's our stock levels.")
print_stock()

# Each time we sell stock, or order more, we define rules as follows:
# * if we have 0 outfits in stock, order 1 jeans and 1 tshirt
# * if we have 0 jeans in stock, order 1 jeans
# * if we have 0 tshirts in stock, order 1 tshirt

def inventory_changed(me, affected_nodes, node_that_changed, attr_changed, cur_val, prev_val):
    # We will set this function to run whenever the rule (outfit) changes. This
    # change can be triggered either by updating a property on the rule directly
    # (i.e. `kb.rule('outfit(X, Y)').inventory = 1`) or when one of the nodes
    # that feed the rule changes (i.e. `kb.node('tshirt').inventory = 1`)

    if prev_val is not None and cur_val > prev_val and me == node_that_changed:
        
        # More outfits were ordered: behind the scenes, it means we ordered
        # another t-shirt and another jeans.

        for node in affected_nodes:
            node.inventory += cur_val - prev_val

    # Update our own inventory

    me.inventory = min([n.inventory for n in affected_nodes])

    if me.inventory is not None and me.inventory < 1:
        
        # We sold something and are now out of stock.
        # Better order more.

        print('<<< Automatically ordering another jeans because we had 0 stock\n')
        node_that_changed.inventory += 1

    else:

        # We still have sufficient stock. 
        pass


# Set the function to run when the rule's computed value changes
kb.rule(rule_num).on_change = inventory_changed

# Right! Let's sell a jeans.
# Notice how the number of sellable outfits goes down accordingly.

print('>>> Selling one jeans\n')
kb.node('jeans').inventory -= 1

print_stock()

# And another

print('>>> Selling one jeans\n')
kb.node('jeans').inventory -= 1

print_stock()

# And finally, let's sell another jeans, everyone loves jeans.
# This one puts our inventory of jeans to 0; the rule will trigger
# inventory_changed which will automatically order more.

print('>>> Selling one jeans')
kb.node('jeans').inventory -= 1

print_stock()

# We only have 1 outfit to sell (luckily Zincbase ordered more.)
# Let's order another outfit, as in, a set of tshirt and jeans.

print('<<< Manually ordering another outfit set\n')
kb.rule(rule_num).inventory += 1

print_stock()

print('>>> So we have 2 jeans/11 tshirts left to sell (or 2 outfits).')
print('>>> If we sell 1 jeans, we should have only 1 outfit left to sell.')
print('>>> Selling 1 jeans\n')

# Sell 1 more jeans
kb.node('jeans').inventory -= 1

print('After all these transactions, there should be only a single jeans in stock, meaning we can only sell 1 outfit too.\n')

print_stock()

# The same results could totally be obtained using watch functions on individual
# nodes. This was just an example on how to use rules to get there conceptually
# more easily (depending on your thinking mode...)
