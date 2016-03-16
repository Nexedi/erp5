# Reset selections
selection_tool = context.getPortalObject().portal_selections
selection_tool.setSelectionFor('project_module_selection', None)

return "Reset Successfully."
