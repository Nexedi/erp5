import six
# License: GPL
# Author: Lukasz Nowak <lukasz.nowak@ventis.com.pl>
# Copyright 2007 Ventis s. c.

simulations_found = context.Base_getSimulationTree(start_path=start_path)

if len(simulations_found) == 0:
  print 'No simulations related'
else:
  for simulation_root in six.iterkeys(simulations_found):
    print simulation_root
    for simulation in simulations_found[simulation_root]:
      print '\t',simulation.getPath(),simulation.getPortalType(),
      if simulation.getPortalType() == 'Simulation Movement':
        print simulation.getCausalityState(),
      else:
        print 'nostate',
      print simulation.getCategoriesList()

return printed
