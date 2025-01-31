po = me.getCausalityValue(portal_type='Production Order')
if po:
  portal = context.getPortalObject()
  quality_me = portal.portal_catalog.getResultValue(
    portal_type='Manufacturing Execution',
    strict_causality_uid = po.getUid(),
    strict_ledger_uid=portal.portal_categories.ledger.manufacturing.quality_insurance.getUid()
  )
  line_list = quality_me.objectValues(sort_on=(('int_index', 'ascending'), ))
  for line in line_list:
    target = line.getAggregateValue(portal_type=("Quality Control", "Traceability", "Gate", "SMON", "ACOM"), checked_permission='View')
    if target:
      if target.getValidationState() == 'queued':
        target.confirm()
        if target.getPortalType() in ('Gate', 'SMON', 'ACOM'):
          break
