request = context.REQUEST
object_list = context.portal_selections.getSelectionValueList(selection_name=request['listbox_list_selection_name'],
                                                              context=context,
                                                              REQUEST=request)

listbox_dict = request['listbox']

component_dict = {}
for object in object_list:
  component_dict.setdefault(object.destination_portal_type,
                            {})[object.getUid()] = listbox_dict[object.getUrl()]['version_item_list']

failed_import_dict = context.migrateSourceCodeFromFilesystem(component_dict, erase_existing, **kw)

if failed_import_dict:
 failed_import_formatted_list = []
 for name, error in failed_import_dict.iteritems():
  failed_import_formatted_list.append("%s (%s)" % (name, error))

 message = "The following component could not be imported: " + ', '.join(failed_import_formatted_list)
 abort_transaction = True
else:
 message = "All components were successfully imported from filesystem to ZODB. You can now delete them from your instance home."
 abort_transaction=False

return context.Base_redirect('view',
                             keep_items={'portal_status_message': message},
                             abort_transaction=abort_transaction)
