from builtins import str
return str(context.getPortalObject().portal_selections.getSelectionFor(selection_name) is not None)
