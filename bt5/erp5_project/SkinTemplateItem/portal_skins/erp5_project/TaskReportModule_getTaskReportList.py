# Get the Object showed at List Box
return  context.portal_selections.getSelectionValueList(context=context,
                                                        REQUEST=context.REQUEST,
                                                        selection_name='task_report_module_selection')
