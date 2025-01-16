po = me.getCausalityValue(portal_type='Production Order')
if po:
  ME_dict = po.ProductionOrder_getRelatedManufacturingExecutionDict()
  quality_me = ME_dict['quality_execution']

  line_list = quality_me.objectValues(sort_on=(('int_index', 'ascending'), ))
  for line in line_list:
    target = line.getAggregateValue(portal_type=("Quality Control", "Traceability", "Gate", "SMON", "ACOM"), checked_permission='View')
    if target:
      if target.getValidationState() == 'queued':
        target.confirm()
        if target.getPortalType() in ('Gate', 'SMON', 'ACOM'):
          break
