from builtins import str
gadget_selection = context.Base_getListboxGadgetSelectionName\
(context.REQUEST.get('box_relative_url', ''))

gadget_preference_dict = context.restrictedTraverse(context.\
REQUEST.get('box_relative_url', '')).KnowledgeBox_getDefaultPreferencesDict()


preference_destination_decision_title = (str(gadget_preference_dict.\
get('listbox_destination_decision_title', None) or ''))

preference_source_project_title = (str(gadget_preference_dict.\
get('listbox_source_project_title', None) or ''))


context.portal_selections.setSelectionParamsFor(gadget_selection,\
{'source_project_title': preference_source_project_title,\
'destination_decision_title': preference_destination_decision_title})


return gadget_selection
