"""
  Allow to reuse an existing user from another instance.
"""
translateString = context.Base_translateString
portal = context.getPortalObject()
request = context.REQUEST

kw = {}
kw['start_date'] = request.get('start_date', None)
kw['stop_date'] = request.get('stop_date', None)
kw['group'] = request.get('field_my_group', None)
kw['function'] = request.get('field_my_function', None)
kw['activity'] = request.get('field_my_activity', None)
kw['title'] = request.get('field_my_title', None)
kw['description'] = request.get('field_my_description', None)

# XXX(lucas): Remove DateTime, because XML-RPC can not handle it.
request.form['start_date'] = ""
request.REQUEST.form['stop_date'] = ""

if context.getReference():
  portal_status_message = translateString('User has login already.')
elif not context.WizardTool_isPersonReferencePresent(reference):
  portal_status_message = translateString('User does not exist yet.')
else:
  # create a local copy
  context.edit(reference=reference)

  # create local assignment
  tag = '%s_reuse_create_assignment' % context.getId()
  context.activate(tag=tag).Person_createAssignment(**kw)

  # create a global account
  if 1:#portal.portal_wizard.isSingleSignOnEnabled():
    context.activate(after_tag=tag).Person_synchroniseExistingAccountWithInstance()

  # create a global account
  context.Person_synchroniseExistingAccountWithInstance()
  portal_status_message = translateString('Status changed.')

# redirect appropriately
context.Base_redirect(form_id=form_id,
                      keep_items={'portal_status_message': portal_status_message})
