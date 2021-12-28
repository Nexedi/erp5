if context.getStartDate():
  kw = {
    'portal_type': 'Pay Sheet Transaction',
    'source_section_uid': context.getDestinationUid(),
    'delivery.start_date': dict(range='ngt', query=context.getStartDate()),
    'delivery.stop_date': dict(range='nlt', query=context.getStartDate()),
    'simulation_state': ('draft', 'planned', 'confirmed', 'started', 'stopped','delivered')
  }
  return context.portal_catalog.getResultValue(**kw)
