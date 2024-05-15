portal = context.getPortalObject()
request = context.REQUEST
Base_translateString = portal.Base_translateString
preserved_parameter_dict = {}

Base_doAction = select_action.split()
doAction0 = Base_doAction[0]

kw['keep_items'] = preserved_parameter_dict

if doAction0 == 'add':
  return context.Folder_create(' '.join(Base_doAction[1:]), **kw)

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
    return new_content.Base_redirect(keep_items=preserved_parameter_dict)
  else:
    message = Base_translateString("Template does not exist.")

else:
  message = Base_translateString('Error: the action "%s" is not recognised.' % (doAction0, ))

request.RESPONSE.setStatus(400)
return context.Base_renderForm(dialog_id, message=message, level='error')
