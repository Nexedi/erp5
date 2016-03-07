try:
  return [('Do Nothing', '')] + [x for x in context.getPortalObject().portal_solvers.getDeliverySolverTranslatedItemList() \
      if x[1] in context.getSolverValue().getDeliverySolverList()]
except AttributeError: # FIXME too wide
  return [('Do Nothing', '')]
