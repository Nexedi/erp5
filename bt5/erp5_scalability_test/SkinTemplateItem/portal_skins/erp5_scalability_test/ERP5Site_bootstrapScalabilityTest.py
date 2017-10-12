# Script that creates "user_number" user for scalabiility tests:
# creates and validates persons
# adds assignment and starts it
# creates user (login credentials)
# password is random for every call
# creates the scalability users file

from DateTime import DateTime
import random
import string

request = context.REQUEST
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

now = DateTime()
status_code = 0
error_message = "No error."

configurator = portal_catalog.getResultValue(
                  portal_type = "Business Configuration",
                  id = "default_standard_configuration",
                  title = "Small And Medium Business")

if configurator == None or not configurator.contentValues(portal_type='Configuration Save'):
  error_message = "Could not find the scalability business configuration object. Standard configuration not installed?"
  return {'status_code' : 1, 'error_message': error_message, 'password' : None }

user_number = request.get('user_number')
if user_number is None: return {'status_code' : 1, 'error_message': "Parameter 'user_number' is required.", 'password' : None }
password = ''.join(random.choice(string.digits + string.letters) for i in xrange(10))

try:
  organisation = portal_catalog.getResultValue(
                    portal_type="Organisation",
                    title = 'Scalability company')
  if organisation is None:
    error_message = "Could not find the scalability organisation. Standard configuration not installed?"
    return {'status_code' : 1, 'error_message': error_message, 'password' : None }
  organisation = organisation.getObject().getRelativeUrl()

  for i in xrange(0, int(user_number)):
    user_id = "scalability_user_%i" % i
    person = portal_catalog.getResultValue(
                    portal_type="Person",
                    id = user_id)
    if person is None:
      person = portal.person_module.newContent(
                      portal_type = "Person",
                      id = user_id,
                      first_name = "scalability",
                      last_name = "user %i" % i,
                      function_list = ["company/manager"],
      )
      person.validate()
    assignements = person.objectValues(portal_type = 'Assignment')
    for assignement in assignements:
      if assignement.getId() == "assignment_%s" % user_id:
        person.deleteContent(id = "assignment_%s" % user_id)
    assignment = person.newContent(
                    portal_type = "Assignment",
                    id = "assignment_%s" % user_id,
                    title = "user assignment",
                    function_list = ["company/manager"],
                    destination_relative_url = organisation,
                    destination = organisation,
                    group_list = ["my_group"],
                    start_date = now,
                    stop_date = DateTime(3000, 1, 1)
    )
    assignment.open()
    users = person.objectValues(portal_type = 'ERP5 Login')
    for user in users:
      if user.getId() == "login_%s" % user_id:
        person.deleteContent(id = "login_%s" % user_id)
    user = person.newContent(
                    portal_type = "ERP5 Login",
                    id = "login_%s" % user_id,
                    default_reference = user_id,
                    password = password,
    )
    user.validate()
except Exception as e:
  status_code = 1
  error_message = str(e)

return {'status_code' : status_code, 'error_message': error_message, 'password' : password }
