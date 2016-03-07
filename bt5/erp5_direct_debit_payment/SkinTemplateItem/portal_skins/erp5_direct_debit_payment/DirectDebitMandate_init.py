"""Initialize an unique reference on direct debit mandate, and set an initial version.
"""
reference = context.getPortalObject().portal_ids.generateNewId(
  id_group='direct_debit_mandate.reference',
  id_generator='uid',
  default=1)

context.setReference('%05d' % reference)
context.setVersion('001')
