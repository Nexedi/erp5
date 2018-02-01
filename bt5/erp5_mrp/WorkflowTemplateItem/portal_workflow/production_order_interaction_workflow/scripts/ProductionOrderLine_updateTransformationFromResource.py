production_order = state_change['object']
line_list = production_order.objectValues(portal_type=("Production Order Line", "Manufacturing Order Line"))
for line in line_list:
  line.ProductionOrderLine_setTransformationFromResource()
