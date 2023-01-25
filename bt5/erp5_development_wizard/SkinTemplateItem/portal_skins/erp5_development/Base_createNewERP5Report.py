"""
  Create new report dialog

  GOOD:
  - dialog provides format options

  TODO:
  - where are the report actions ??? Do I have to do it manually... I hope not!
"""

MARKER = ['', None]

portal = context.getPortalObject()
portal_skins = portal.portal_skins

if create_skin_id not in MARKER:
  # create skin
  skin_folder = context.Base_createSkinFolder(create_skin_id)
else:
  skin_folder = getattr(portal_skins, selected_skin_id)

erp5_report_form_id = erp5_report_form_id.replace(' ', '')
form_action_portal_type = action_portal_type.replace(' ', '')
form_id = '%s_view%sReport' %(form_action_portal_type, erp5_report_form_id)

dialog_form_id = None
if create_configure_dialog:
  # copy an existing form and just set method to new form
  dialog_form_id = '%sDialog' %form_id
  source_form_id = "Folder_generateWorkflowReportDialog"
  cb_copy_data = context.portal_skins.erp5_core.manage_copyObjects([source_form_id])
  skin_folder.manage_pasteObjects(cb_copy_data)
  skin_folder.manage_renameObjects(ids=[source_form_id], new_ids=[dialog_form_id])
  # set title, and actions
  form_object = getattr(skin_folder, dialog_form_id)
  context.editForm(form_object,{'title': erp5_report_form_title,
                                'action': form_id})

if sql_expression not in MARKER:
  # create ZSQL method
  listbox_list_method_id = '%s_zGet%sList' %(form_action_portal_type, erp5_report_form_id)
  skin_folder.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod(
                        listbox_list_method_id,
                        listbox_list_method_id,
                        'erp5_sql_connection',
                        '',
                        sql_expression)
  zsql_method = getattr(skin_folder, listbox_list_method_id)
  zsql_method.manage_advanced(max_rows=1000,
                              max_cache=100,
                              cache_time=0,
                              class_name='ZSQLBrain',
                              class_file='ZSQLCatalog.zsqlbrain',
                              direct=None,
                              REQUEST=None)

if python_expression not in MARKER:
  # create Python method
  listbox_list_method_id = '%s_get%sList' %(form_action_portal_type, erp5_report_form_id)
  skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id=listbox_list_method_id)
  script = getattr(skin_folder, listbox_list_method_id)
  script.ZPythonScript_edit('**kw', python_expression)

# add report form
skin_folder.manage_addProduct['ERP5Form'].addERP5Form(form_id)
form_object = getattr(skin_folder, form_id)
context.editForm(form_object,
                 {'title': erp5_report_form_title,
                  'pt': 'form_list',})

# create real ERP5 Form and configure it ..
listbox_id = 'listbox'
form_object.manage_addProduct['Formulator'].manage_addField(
              id=listbox_id,
              fieldname='ListBox',
              title='Listbox')
# listbox is in bottom group
form_object.move_field_group(listbox_id, 'left', 'bottom')
listbox = getattr(form_object, listbox_id)
listbox.manage_edit_xmlrpc({'selection_name': form_id,
                            'columns': [[x, x] for x in listbox_column_id_list],
                            'list_method': context.getMethodObject(listbox_list_method_id)
                            })

if dialog_form_id is not None:
  form_id = dialog_form_id
if portal_type_action:
  # create action
  portal.portal_types[action_portal_type].newContent(
           portal_type='Action Information',
           reference=form_id,
           title=erp5_report_form_title,
           action='string:${object_url}/%s' %form_id,
           action_permission='View',
           action_type='object_report',
           visible=1,
           priority=1.0)

context.REQUEST.RESPONSE.redirect('%s/portal_skins/%s/manage_main' \
                                  %(context.getPortalObject().absolute_url(),
                                    selected_skin_id))
