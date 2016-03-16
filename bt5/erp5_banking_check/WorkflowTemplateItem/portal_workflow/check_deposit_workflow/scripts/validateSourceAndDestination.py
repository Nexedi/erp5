transaction = state_change['object']

# Check getBaobabSource and getBaobabDestination
transaction.Base_checkBaobabSourceAndDestination()

context.validateConsistency(state_change)
