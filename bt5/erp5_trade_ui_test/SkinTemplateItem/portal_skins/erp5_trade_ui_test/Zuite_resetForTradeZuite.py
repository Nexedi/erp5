# Reset selections
selection_tool = context.getPortalObject().portal_selections
selection_tool.setSelectionFor('sale_order_selection', None)

return "Reset Successfully."
