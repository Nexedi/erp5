"""Returns an unique reference for this payment transaction. If it does not already have a reference, a new one is generated.
"""
context.getTypeBasedMethod('generateReference')()
return context.getReference()
