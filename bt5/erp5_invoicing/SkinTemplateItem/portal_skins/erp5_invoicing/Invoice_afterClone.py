"""Reset references on copied transactions.
"""
context.setReference(None)
# invoice is a delivery so call generic afterClone script
context.Delivery_afterClone()
