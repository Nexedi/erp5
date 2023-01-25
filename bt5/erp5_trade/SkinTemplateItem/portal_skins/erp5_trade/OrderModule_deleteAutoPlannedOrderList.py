"""Delete all orders in auto_planned state.
"""
id_list = [order.getId() for order in
            context.searchFolder(portal_type=context.getPortalOrderTypeList(),
                                 simulation_state=('auto_planned',))]
if id_list:
  context.manage_delObjects(id_list)
