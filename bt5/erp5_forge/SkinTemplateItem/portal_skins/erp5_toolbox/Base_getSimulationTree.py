# License: GPL
# Author: Lukasz Nowak <lukasz.nowak@ventis.com.pl>
# Copyright 2007 Ventis s. c.
# SYNOPSIS
# This script extracts simulations (Applied Rule and Simulation Movement) for context.
# If start_path is given it instead extracts tree with root as given start_path.


def getByRecurse(obj):
  rv = []
  for o in [q.getObject() for q in obj.searchFolder()]:
    rv.append(getByRecurse(o))
  return rv

def getFromCatalog(start_path):
  return [x.getObject() for x in context.portal_catalog(
    portal_type=('Applied Rule','Simulation Movement',),
    path=[start_path, start_path+'/%'],
    sort_on=(('path','ascending','char'),)
  )]

if start_path is None:
  # we have to detect simulations
  if context.getPortalType() in ['Simulation Movement','Applied Rule']:
    # we are run from simulation, its our root
    start_paths = [context.getPath(),]
  else:
    # hm, it might be, that our context have simulations in relate objects?
    start_paths = [x.getPath() for x in context.portal_categories.getRelatedValueList(context,portal_type=['Simulation Movement','Applied Rule'])]
else:
  start_paths = [start_path,]
if start_paths == []:
  # we are in no simulation related object
  return []

related_simulations = {}
for start_path in start_paths:

  related_simulations[start_path] = getFromCatalog(start_path)

return related_simulations
