"""
  Puts all the arguments from advanced search dialog form together as
  a parseable search string. Set it in the selection so it can be used
  in search form.
"""
portal = context.getPortalObject()
searchabletext = context.Base_assembleSearchString()

selection_id = 'search_advanced_dialog_selection'
selection_object = portal.portal_selections.getSelectionParamsFor(selection_id, {})
if selection_object:
  # update
  selection_object['searchabletext'] = searchabletext
else:
  selection_object = {'searchabletext': searchabletext}

selection_object['list_style'] = 'search'
portal.portal_selections.setSelectionParamsFor(selection_id, \
                                               selection_object)
return context.Base_viewAdvancedSearchResultList()
