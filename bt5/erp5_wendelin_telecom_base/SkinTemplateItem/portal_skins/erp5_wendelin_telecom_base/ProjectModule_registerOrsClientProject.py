'''
Creates a Project representing a client project, as well as an associated ERP5 Person
corresponding to the client's user account.

The Person will be given the provided email address,
an active assignment with the appropriate function and project,
as well as an ERP5 Login initialized with a random password that will need to be reset.
'''

import random

portal = context.getPortalObject()

project = context.portal_catalog.getResultValue(
  portal_type='Project',
  # Do not test for title collision
  reference=project_reference,
  validation_state='validated'
)
if project:
  portal_status_message = "Project with reference %s already exists." % project_reference
  kw['keep_items'] = dict(
    portal_status_message=portal_status_message,
    portal_status_level='error'
  )
  return context.Base_redirect(form_id, **kw)

# Email field in action form checks that the email address is valid
# For all other cases, let the caller handle the error
client_user_reference = client_email.split('@')[0]
client_user = context.portal_catalog.getResultValue(
  portal_type='Person',
  reference=client_user_reference,
  validation_state='validated'
)
if client_user:
  portal_status_message = "Person with reference %s already exists." % client_user_reference
  kw['keep_items'] = dict(
    portal_status_message=portal_status_message,
    portal_status_level='error'
  )
  return context.Base_redirect(form_id, **kw)

project = portal.project_module.newContent(
  portal_type='Project',
  reference=project_reference,
  title=project_title,
)
project.validate()
destination_project = project.getRelativeUrl()

password_length = 20
client_init_password = ''.join(random.SystemRandom().sample(string.ascii_letters + string.digits, password_length))

client_function = 'user'

client_user = portal.person_module.newContent(
  portal_type='Person',
  reference=client_user_reference,
  default_email_text=client_email
)
client_user.newContent(
  portal_type='Assignment',
  title='User for %s' % project_title,
  destination_project=destination_project,
  function=client_function
).open()
client_user.newContent(portal_type='ERP5 Login', reference=client_email, password=client_init_password).validate()
client_user.validate()

portal_status_message = "ORS Client Project successfully registered."
kw['keep_items'] = dict(
  portal_status_message=portal_status_message
)
return context.Base_redirect(form_id, **kw)
