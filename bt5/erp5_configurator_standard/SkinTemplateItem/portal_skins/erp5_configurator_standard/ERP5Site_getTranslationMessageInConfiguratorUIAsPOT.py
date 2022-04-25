message_dict = {}
FUNC_NAME_LIST = ('N_',
                  'Base_translateString',
                  'translateString',
                  )

def safe_get_value(field, key):
  try:
    return field.get_orig_value(key)
  except KeyError:
    return field.get_value(key)

def add_message(message, comment):
  if not message:
    return
  if message in message_dict:
    comment_list = message_dict[message]
  else:
    comment_list = message_dict[message] = []
  if comment not in comment_list:
    comment_list.append(comment)

portal_url = context.portal_url

# Collect skin objects
form_list = []
field_list = []
page_template_list = []
python_script_list = []
def iterate(obj, script=True, form=True, field=True, listbox=True, template=True):
  for i in obj.objectValues():
    if script and i.meta_type=='Script (Python)':
      python_script_list.append(i)
    if form and i.meta_type=='ERP5 Form':
      form_list.append(i)
    elif field and i.meta_type.endswith('Field'):
      field_list.append(i)
    elif template and i.meta_type in ('Page Template',
                         'ERP5 PDF Template',
                         'ERP5 OOo Template'):
      page_template_list.append(i)
    if i.isPrincipiaFolderish:
      iterate(i, form=form, field=field, template=template)

iterate(context.portal_skins.nexedi_express_configuration, form=False)
iterate(context.portal_skins.erp5_generator, template=True, form=False, field=False)
iterate(context.portal_skins.erp5_generator_widgets, template=True, form=False, field=False)

# Collect from ERP5Configurator product.
for message, path in context.Base_findMessageListFromPythonInProduct(FUNC_NAME_LIST):
  if 'ERP5Configurator' in path:
    add_message(message, path)

# Collect workflow transition documents from workflow module.
for document in context.portal_workflow.express_setup_workflow.contentValues():
  if document.portal_type=='Workflow Transition' and document.getTransitionFormId() is not None:
    add_message(document.getTitle(), portal_url.getRelativeContentURL(document))


# Collect title and description of each wizard page.
ui_description = context.portal_skins.nexedi_express_configuration['nexedi_express_configuration_ui_description.sxc']
for page_dict in context.ConfigurationTemplate_readOOCalcFile('nexedi_express_configuration_ui_description.sxc'):
  add_message(page_dict['title'], portal_url.getRelativeContentURL(ui_description))
  add_message(page_dict['description'], portal_url.getRelativeContentURL(ui_description))


#
# ERP5 Form title
#
# Add exceptional form
form_list.append(context.nexedi_express_configuration.ExpressConfiguration_setupEmployeeListForm)
for i in form_list:
  if (i.getId().endswith('_viewFieldLibrary') or
      i.getId().endswith('_viewDialogFieldLibrary') or
      i.getId().endswith('_viewReportFieldLibrary') or
      i.getId().endswith('_FieldLibrary')
      ):
    continue
  add_message(i.title, portal_url.getRelativeContentURL(i))

# Add exceptional fields
for i in field_list:
  add_message(safe_get_value(i, 'title'), portal_url.getRelativeContentURL(i))
  if i.has_value('default') and not i.get_tales('default'):
    add_message(safe_get_value(i, 'default'), portal_url.getRelativeContentURL(i))

# Other Exceptions
accounting_period_description = context.portal_skins.nexedi_express_configuration.ExpressConfiguration_setupAccountingForm.your_period_description
add_message(accounting_period_description.get_orig_value('default'), portal_url.getRelativeContentURL(accounting_period_description))


#
# Page Template
#
Base_findStaticTranslationText = context.Base_findStaticTranslationText
for i in page_template_list:
  for m in Base_findStaticTranslationText(i, FUNC_NAME_LIST):
    add_message(m, portal_url.getRelativeContentURL(i))


#
# Python script
#
Base_getFunctionFirstArgumentValue = context.Base_getFunctionFirstArgumentValue
for i in python_script_list:
  source = i.body()
  for func_name in FUNC_NAME_LIST:
    call_func_name = '%s(' % func_name
    if call_func_name in source:
      for m in Base_getFunctionFirstArgumentValue(func_name, source):
        add_message(m, portal_url.getRelativeContentURL(i))


#
# Currency List
#
for row in context.ConfigurationTemplate_readOOCalcFile('standard_currency_list.ods'):
  add_message(row['currency'], portal_url.getRelativeContentURL(context.portal_skins.erp5_generator['standard_currency_list.ods']))


#
# Output
#
def formatText(string):
  line_list = string.split('\n')
  length = len(line_list)
  if length==1:
    return '"%s"' % string
  else:
    return '\n'.join(['""']+[formatText(i) for i in line_list])


MESSAGE_TEMPLATE = '''\
%s
msgid %s
msgstr ""
'''
message_list = message_dict.keys()
message_list.sort()
for message in message_list:
  comment_list = message_dict[message]
  comment_list.sort()
  comment = '\n'.join([('#: %s' % i) for i in comment_list])
  print(MESSAGE_TEMPLATE % (comment, formatText(message)))

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')

return printed
