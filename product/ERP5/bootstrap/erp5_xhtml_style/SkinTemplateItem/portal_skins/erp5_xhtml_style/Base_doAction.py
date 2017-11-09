portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
preserved_parameter_dict = {
  'form_id': form_id,
  'cancel_url': cancel_url,
  'md5_object_uid_list': md5_object_uid_list,
  'list_selection_name': list_selection_name,
}
request = context.REQUEST

if select_action is None:
  select_action = request.form["Base_doAction"]

# prevent lose checked itens after select action
# For backward compatibility, do nothing if
# Base_updateListboxSelection cannot be found.
Base_updateListboxSelection = getattr(context, 'Base_updateListboxSelection', None)
if Base_updateListboxSelection is not None:
  Base_updateListboxSelection()

Base_doAction = select_action.split()
if len(Base_doAction) == 0:
  return
doAction0 = Base_doAction[0]

kw.update(request.form)
# Using Base_updateListboxSelection instead
#context.ERP5Site_prepareAction(**kw)

# If this is an object, a workflow or a folder, then jump to that view
if doAction0 in ('object', 'workflow', 'folder'):
  redirect_url = ' '.join(Base_doAction[1:])
  if doAction0 == 'object':
    kw['dialog_category'] = 'object_action'
# Otherwise, check if this is an automatic menu (add)
elif doAction0 == 'add':
  return context.Folder_create(' '.join(Base_doAction[1:]),
                               preserved_parameter_dict,
                               **kw)
# Otherwise, check if this is an automatic menu (template)
elif doAction0 == 'template':
  template_relative_url = ' '.join(Base_doAction[1:])
  template = context.getPortalObject().restrictedTraverse(template_relative_url)
  if template is not None:
    preference = template.getParentValue()
    preference.manage_copyObjects(ids=[template.getId()], REQUEST=request, RESPONSE=None)
    new_content_list = context.manage_pasteObjects(request['__cp'])
    new_content_id = new_content_list[0]['new_id']
    new_content = context[new_content_id]
    new_content.makeTemplateInstance()
    preserved_parameter_dict['portal_status_message'] = Base_translateString("Template created.")
    redirect_url = new_content.absolute_url()
  else:
    preserved_parameter_dict['portal_status_message'] = Base_translateString("Template does not exist.")
    redirect_url = context.absolute_url()
else:
  redirect_url = request['ACTUAL_URL']
  preserved_parameter_dict['portal_status_message'] = Base_translateString('Error: the action "%s" is not recognised.' % (doAction0, ))

return context.ERP5Site_redirect(redirect_url, keep_items=preserved_parameter_dict, **kw)
