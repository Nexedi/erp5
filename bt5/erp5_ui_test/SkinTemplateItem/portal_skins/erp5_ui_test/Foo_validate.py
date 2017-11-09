"""Validate Foo"""
# for security
assert context.getPortalType() == 'Foo'
context.validate()
return context.getSimulationStateTitle()
