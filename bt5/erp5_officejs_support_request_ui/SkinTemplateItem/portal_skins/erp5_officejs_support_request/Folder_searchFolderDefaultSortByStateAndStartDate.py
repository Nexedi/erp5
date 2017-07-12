if 'sort_on' not in kw:
  kw['sort_on'] = [('simulation_state', 'descending'), ('delivery.start_date', 'descending')]
else:
  if 'simulation_state' not in [x[0] for x in kw['sort_on']]:
    kw['sort_on'] = list(kw['sort_on']) + [('simulation_state', 'descending')]
  if 'delivery.start_date' not in [x[0] for x in kw['sort_on']]:
    kw['sort_on'] = list(kw['sort_on']) + [('delivery.start_date', 'descending')]

return context.searchFolder(**kw)
