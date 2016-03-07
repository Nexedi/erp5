# Base_updateListboxSelection cannot be found.
Base_updateListboxSelection = getattr(context, 'Base_updateListboxSelection', None)
if Base_updateListboxSelection is not None:
  Base_updateListboxSelection()

context.REQUEST.set("proxy_listbox_id", select_dialog )

# Reset selection when changing the listbox (request parameters will be kept)
stool = context.getPortalObject().portal_selections
stool.setSelectionFor("Base_viewRelatedObjectList", None)
return context.Base_viewRelatedObjectList(REQUEST=context.REQUEST)
