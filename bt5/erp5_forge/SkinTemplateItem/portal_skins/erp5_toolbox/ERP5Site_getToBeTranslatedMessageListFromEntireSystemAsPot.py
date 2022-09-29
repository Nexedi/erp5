from Products.ERP5Type.Utils import getMessageIdWithContext
message_dict = {}

def add_message(message, comment):

  if not message:
    return
  message = message.decode('utf-8')
  if message in message_dict:
    comment_list = message_dict[message]
  else:
    comment_list = message_dict[message] = []
  if comment not in comment_list:
    comment_list.append(comment)



portal_url = context.portal_url

# Collect skin objects
python_script_list = []
form_list = []
listbox_list = []
page_template_list = []
def iterate(obj):
  for i in obj.objectValues():
    if i.meta_type=='Script (Python)':
      python_script_list.append(i)
    elif i.meta_type=='ERP5 Form':
      form_list.append(i)
    elif i.meta_type=='ListBox' or i.id=='listbox':
      listbox_list.append(i)
    elif i.meta_type in ('Page Template',
                         'ERP5 PDF Template',
                         'ERP5 OOo Template'):
      page_template_list.append(i)
    if i.isPrincipiaFolderish:
      iterate(i)
iterate(context.portal_skins)

# Collect python script from workflow objects.
for workflow in context.portal_workflow.objectValues():
  for i in workflow.getScriptValueDict().values():
    if i.meta_type=='Script (Python)':
      python_script_list.append(i)

#
# Python Script
#
FUNC_NAME_LIST = ('N_',
                  'Base_translateString',
                  'translateString',
                  )

Base_getFunctionFirstArgumentValue = context.Base_getFunctionFirstArgumentValue
for i in python_script_list:
  source = i.body()
  for func_name in FUNC_NAME_LIST:
    call_func_name = '%s(' % func_name
    if call_func_name in source:
      for m in Base_getFunctionFirstArgumentValue(func_name, source):
        add_message(m, portal_url.getRelativeContentURL(i))

#
# Python in Products
#
for message, path in context.Base_findMessageListFromPythonInProduct(FUNC_NAME_LIST):
  add_message(message, path)

#
# ERP5 Form title, Field title and editable Field description
#
for i in form_list:
  if (i.getId().endswith('FieldLibrary')):
    continue
  add_message(i.title, portal_url.getRelativeContentURL(i))
  for group, list_ in i.groups.items():
    if group == 'hidden':
      continue
    for j in (i[x] for x in list_):
      add_message(j.get_value('title'), portal_url.getRelativeContentURL(j))
      if j.get_value('editable'):
        add_message(j.get_value('description'), portal_url.getRelativeContentURL(j))

#
# ListBox title, columns
#
for i in listbox_list:
  if i.get_tales('title')=='':
    add_message(i.title(), portal_url.getRelativeContentURL(i))
  for value, label in i.get_value('columns') or ():
    add_message(label, portal_url.getRelativeContentURL(i))
  for value, label in i.get_value('all_columns') or ():
    add_message(label, portal_url.getRelativeContentURL(i))

#
# Page Template
#
Base_findStaticTranslationText = context.Base_findStaticTranslationText
for i in page_template_list:
  for m in Base_findStaticTranslationText(i, FUNC_NAME_LIST):
    add_message(m, portal_url.getRelativeContentURL(i))

#
# Workflow
#
for i in context.portal_workflow.objectValues():
  add_message(i.title_or_id(), portal_url.getRelativeContentURL(i))

  state_value_list = i.getStateValueList()
  if not state_value_list:
    continue
  for s in state_value_list:
    if s.getTitle():
      # adding a context in msg_id for more precise translation
      msg_id = getMessageIdWithContext(s.getTitle(),'state',i.getId())
      add_message(msg_id, portal_url.getRelativeContentURL(s))
      # also use state title as msg_id for compatibility
      add_message(s.getTitle(), portal_url.getRelativeContentURL(s))

  transition_value_list = i.getTransitionValueList()
  if not transition_value_list:
    continue
  for t in transition_value_list:
    if t.getActionName():
      #adding a context in msg_id for more precise translation
      msg_id = getMessageIdWithContext(t.getActionName(),'transition',i.getId())
      add_message(msg_id, portal_url.getRelativeContentURL(t))
      # also use action box name as msg_id for compatibility
      add_message(t.getActionName(), portal_url.getRelativeContentURL(t))
    if t.getTitle():
      #adding a context in msg_id for more precise translation
      msg_id = getMessageIdWithContext(t.getTitle(),'transition',i.getId())
      add_message(msg_id, portal_url.getRelativeContentURL(t))
      # also use transition title as msg_id for compatibility
      add_message(t.getTitle(), portal_url.getRelativeContentURL(t))
  for worklist in i.getWorklistValueList():
    add_message(worklist.getActionName(), portal_url.getRelativeContentURL(worklist))


#
# Portal Type
#
for i in context.portal_types.objectValues():
  add_message(i.id, 'portal type')


#
# Action
#
for action_title, action_provider_id in context.Base_getActionTitleListFromAllActionProvider(context.getPortalObject()):
  add_message(action_title, action_provider_id)

#
# ZODB Property Sheet
#
for property_sheet in context.portal_property_sheets.objectValues():
  for property_ in property_sheet.objectValues():
    if property_.getId().endswith('constraint'):
      for key, value in property_.showDict().items():
        if key.startswith('message_'):
          add_message(value, portal_url.getRelativeContentURL(property_))

#
# Output
#
def formatString(string):
  line_list = string.split('\n')
  length = len(line_list)
  if length==1:
    return '"%s"' % string.replace('"', '\\"')
  else:
    return '\n'.join(['""']+[formatString(i) for i in line_list])

print '''msgid ""
msgstr "Content-Type: text/plain; charset=UTF-8"

'''

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
  print MESSAGE_TEMPLATE % (comment, formatString(message))

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-disposition', 'attachment;filename=translation.pot')
RESPONSE.setHeader('Content-Type', 'text/x-gettext-translation-template;charset=utf-8')

return printed
