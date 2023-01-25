portal = context.getPortalObject()
skin_folder = getattr(portal.portal_skins, skin_folder)

type_name = portal_type.replace(' ', '')
report_name_part = ''.join([part.capitalize() for part in report_name.split()])
dialog_form_name = '%s_view%sReportDialog' % (type_name, report_name_part)
report_form_name = '%s_view%sReport' % (type_name, report_name_part)
report_section_form_name = '%s_view%sReportSection' % (type_name,
    report_name_part)
get_report_section_script_name = '%s_get%sReportSectionList' % (type_name,
    report_name_part)
get_line_list_script_name = '%s_get%sLineList' % (type_name, report_name_part)
action_id = "%s_report" % '_'.join([part.lower() for part in report_name.split()])

# Create the dialog
skin_folder.manage_addProduct['ERP5Form'].addERP5Form(dialog_form_name, report_name)
dialog = getattr(skin_folder, dialog_form_name)
dialog.manage_settings(
    dict(field_title=dialog.title,
         field_name=dialog.name,
         field_description=dialog.description,
         field_action=report_form_name,
         field_action_title=dialog.action_title,
         field_update_action=dialog.update_action,
         field_update_action_title=dialog.update_action_title,
         field_enctype=dialog.enctype,
         field_encoding=dialog.encoding,
         field_stored_encoding=dialog.stored_encoding,
         field_unicode_mode=dialog.unicode_mode,
         field_method=dialog.method,
         field_row_length=str(dialog.row_length),
         field_pt='form_dialog',
         field_edit_order=[]))

if use_from_date_at_date:
  dialog.manage_addField(
           id='your_from_date',
           fieldname='ProxyField',
           title='')
  dialog.your_from_date.manage_edit_xmlrpc(
      dict(form_id='Base_viewDialogFieldLibrary',
           field_id='your_from_date'))
  dialog.manage_addField(
           id='your_at_date',
           fieldname='ProxyField',
           title='')
  dialog.your_at_date.manage_edit_xmlrpc(
      dict(form_id='Base_viewDialogFieldLibrary',
           field_id='your_at_date'))

dialog.manage_addField(
         id='your_portal_skin',
         fieldname='ProxyField',
         title='')
dialog.your_portal_skin.manage_edit_xmlrpc(
    dict(form_id='Base_viewDialogFieldLibrary',
         field_id='your_portal_skin'))
dialog.manage_addField(
         id='your_format',
         fieldname='ProxyField',
         title='')
dialog.your_format.manage_edit_xmlrpc(
    dict(form_id='Base_viewDialogFieldLibrary',
         field_id='your_format'))
dialog.manage_addField(
         id='your_deferred_style',
         fieldname='ProxyField',
         title='')
dialog.your_deferred_style.manage_edit_xmlrpc(
    dict(form_id='Base_viewDialogFieldLibrary',
         field_id='your_deferred_style'))

# Associate the dialog with type information
type_information = portal.portal_types.getTypeInfo(portal_type)
max_priority = 0
action_list = type_information.contentValues(portal_type='Action Information')
if action_list:
  max_priority = max([ai.getFloatIndex() or 0 for ai in action_list])

type_information.addAction(
    action_id,
    report_name,
    "string:${object_url}/%s" % dialog_form_name,
    '',
    'View',
    'object_jio_report',
    priority=max_priority+1,)

type_information.addAction(
    action_id.replace('_report', '_export'),
    report_name,
    "string:${object_url}/%s?your_portal_skin=ODS&your_format=" % dialog_form_name,
    "python: getattr(portal.portal_skins, 'erp5_ods_style', None) is not None",
    'View',
    'object_jio_exchange',
    priority=max_priority+1,)


# Associate the dialog with type information in business template meta data
if context.getPortalType() == 'Business Template' and \
     context.getInstallationState() != 'installed':
  context.setTemplateActionPathList(
    sorted(
      tuple(context.getTemplateActionPathList()) +
      ('%s | %s' % (portal_type, action_id),
       '%s | %s' % (portal_type, action_id.replace('_report', '_export')))))

# Create the report
skin_folder.manage_addProduct['ERP5Form'].addERP5Report(report_form_name, report_name)
report = getattr(skin_folder, report_form_name)
report.manage_settings(
  dict(field_title=report.title,
       field_name=report.name,
       field_description=report.description,
       field_action=report_form_name,
       field_action_title=report.action_title,
       field_update_action=report.update_action,
       field_update_action_title=report.update_action_title,
       field_enctype=report.enctype,
       field_encoding=report.encoding,
       field_stored_encoding=report.stored_encoding,
       field_unicode_mode=report.unicode_mode,
       field_method=report.method,
       field_row_length=str(report.row_length),
       field_pt='report_view',
       field_report_method=get_report_section_script_name,
       field_edit_order=[]))

skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
                    report_section_form_name, report_name)
report_section_form = getattr(skin_folder, report_section_form_name)
report_section_form.manage_settings(
  dict(field_title=report_section_form.title,
       field_name=report_section_form.name,
       field_description=report_section_form.description,
       field_action='',
       field_action_title=report_section_form.action_title,
       field_update_action=report_section_form.update_action,
       field_update_action_title=report_section_form.update_action_title,
       field_enctype=report_section_form.enctype,
       field_encoding=report_section_form.encoding,
       field_stored_encoding=report_section_form.stored_encoding,
       field_unicode_mode=report_section_form.unicode_mode,
       field_method=report_section_form.method,
       field_row_length=str(report_section_form.row_length),
       field_pt='form_view',
       field_report_method=get_report_section_script_name,
       field_edit_order=[]))

report_section_form.manage_addField(
         id='listbox',
         fieldname='ProxyField',
         title='')
report_section_form.listbox.manage_edit_xmlrpc(
    dict(form_id='Base_viewFieldLibrary',
         field_id='my_view_mode_listbox'))
report_section_form.move_field_group(('listbox',), 'left', 'bottom')

report_section_form.listbox.manage_edit_surcharged_xmlrpc(
  dict(selection_name=('_'.join((portal_type + report_name).split())).lower() + '_selection',
       title=report_name,
       # XXX this must be a Method, but as far as I know, we cannot set list
       # method in restricted environment
     # list_method=get_line_list_script_name
       ))

if use_from_date_at_date:
  report.manage_addField(
           id='your_from_date',
           fieldname='ProxyField',
           title='')
  report.your_from_date.manage_edit_xmlrpc(
      dict(form_id='Base_viewReportFieldLibrary',
           field_id='your_from_date'))
  report.manage_addField(
           id='your_at_date',
           fieldname='ProxyField',
           title='')
  report.your_at_date.manage_edit_xmlrpc(
      dict(form_id='Base_viewReportFieldLibrary',
           field_id='your_at_date'))

# Create the report section script
skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(
    get_report_section_script_name)
script = getattr(skin_folder, get_report_section_script_name)

get_param_part = ''
if use_from_date_at_date:
  get_param_part = 'from_date = request.get("from_date")\n'\
                   'at_date = request.get("at_date")'

script.ZPythonScript_edit('',
"""from Products.ERP5Form.Report import ReportSection
portal = context.getPortalObject()
request = container.REQUEST
%s

return [ReportSection(form_id='%s',
                      path=context.getPhysicalPath())]
""" % (get_param_part, report_section_form_name))


# Create the script to get list of lines
skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(
    get_line_list_script_name)
script = getattr(skin_folder, get_line_list_script_name)
params = '**kw'
if use_from_date_at_date:
  params = 'from_date=None, at_date=None, **kw'

script.ZPythonScript_edit(params,
"""from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

# TODO: get list of lines here

return [Object(uid='new_',
               title='Nothing',
              )]
""")


return context.Base_redirect(form_id,
    keep_items=dict(portal_status_message=
      context.Base_translateString('Report created.')))
