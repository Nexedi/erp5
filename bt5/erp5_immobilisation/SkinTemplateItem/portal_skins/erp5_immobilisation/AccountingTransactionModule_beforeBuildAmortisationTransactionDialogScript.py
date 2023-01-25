from ZTUtils import make_query

my_selection_name='accounting_module_build_amortisation_selection'
if selection_name == my_selection_name:
  # Update the selection by adding new selected objects to
  # the list of already selected objects
  selected_uids = context.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)

  # Then take the full list of selected objects
  # selection_method should be the same method as the one used in listbox,
  # most of the time it is context.portal_catalog or context.searchFolder
  object_list= [x.getObject() for x in context.portal_selections.getSelectionValueList(selection_name,selection_method=context.portal_catalog)]
  # object_list is the list of selected objects, or it is the full list of objects
  # if there is not any object selected
else:
  object_list = []

item_uid_list = [x.getUid() for x in object_list]

url_params = make_query(form_id=form_id,
                        cancel_url=cancel_url,
                        item_uid_list=item_uid_list)
redirect_url = '%s/AccountingTransactionModule_buildAmortisationTransactionDialog?%s' %\
                          (context.absolute_url(), url_params)
context.REQUEST[ 'RESPONSE' ].redirect(redirect_url)
