"""Adds the payment transaction group to the already aggregated items on this line.

Also ensures that the payment transaction has a reference.

This script has a proxy role to be able to modify delivered lines and to call generateReference.
"""
portal = context.getPortalObject()

assert context.getPortalType() in portal.getPortalAccountingMovementTypeList()

context.setDefaultActivateParameterDict({"activate_kw": activate_kw})
context.setAggregate(aggregate, portal_type='Payment Transaction Group')
context.getParentValue().getTypeBasedMethod('generateReference')()
