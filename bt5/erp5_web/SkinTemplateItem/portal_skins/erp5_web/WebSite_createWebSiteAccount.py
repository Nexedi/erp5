"""
  This script is a sample script skeleton (part of erp5_web)
  which can be used to create user (Person object)

  Notes:
    - the script is normally executed by anonymous user with Manager proxy roles which
      you have to turn on after adjusting this script to your needs.
    - you have to decide if assignment should be opened automatically or
      verified and opened by administrator first
    - you need to adjust group, function and site to your needs
"""

# pylint: disable=unreachable
# since the following code is just an example, we simply raise an exception so that
# it is not executed actually.
raise NotImplementedError

portal = context.getPortalObject()
translateString = context.Base_translateString
website = context.getWebSiteValue()

# Call Base_edit
result, result_type = context.Base_edit(form_id, silent_mode=1, field_prefix='your_')

# Return if not appropriate
if result_type != 'edit':
  return result
kw, _ = result

# Set default values
person_group = kw.get('group', None)
person_function = kw.get('function', None)
person_site = kw.get('site', None)
person_role = kw.get('role', None)
kw.setdefault('reference', kw['default_email_text'])
if 'password_confirm' in kw:
  del kw['password_confirm']

#Check that user doesn't already exists
person_list = [x for x in portal.acl_users.searchUsers(login=kw['reference'], exact_match=True) if 'path' in x]
if person_list:
  msg = translateString("This account already exists. Please provide another email address.")
  kw['portal_status_message'] = msg
  context.REQUEST.form.update(kw)
  return getattr(website, form_id)()

# create Person account
person_module = portal.getDefaultModule(portal_type='Person')
person = person_module.newContent(portal_type='Person', **kw)
person.validate()
# Note: object is not immediately indexed.
# This means that when creating an account the new one will *NOT*
# be available immediately and we should consider sending two email to user
# that 1) his account will be created and when created 2)-> send account info

# Create default career
person.newContent(portal_type='Career',
                  id='default_career',
                  group=person_group,
                  function=person_function,
                  role=person_role)
# Create assignment
assignment = person.newContent(portal_type='Assignment',
                               group=person_group,
                               function=person_function,
                               site=person_site)
assignment.open()

msg = translateString("Your account was successfully created.")
return website.Base_redirect(form_id, keep_items=dict(portal_status_message=msg,
                             editable_mode=0))
