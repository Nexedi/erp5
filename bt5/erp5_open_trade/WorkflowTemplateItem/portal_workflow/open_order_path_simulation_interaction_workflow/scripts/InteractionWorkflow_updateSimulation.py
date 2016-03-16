ob = state_change['object']
while not ob.isOpenOrderType():
  ob = ob.getParentValue()
ob.OpenOrder_updateSimulation()
