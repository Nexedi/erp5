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

user_number = request.get('user_number')
if user_number is None: return {'status_code' : 1, 'error_message': "Parameter 'user_number' is required."}
password = ''.join(random.choice(string.digits + string.letters) for i in xrange(10))

try:
  organisation = portal_catalog.getResultValue(
                    portal_type="Organisation",
                    title = 'Scalability company'
  ).getObject().getRelativeUrl()
  for i in xrange(0, int(user_number)):
    person = portal.person_module.newContent(
                    portal_type = "Person",
                    first_name = "scalability",
                    last_name = "user %i" % i,
                    function_list = ["company/manager"],
    )
    person.validate()
    assignment = person.newContent(
                    portal_type = "Assignment",
                    title = "user assignment",
                    function_list = ["company/manager"],
                    destination_relative_url = organisation,
                    destination = organisation,
                    group_list = ["my_group"],
                    start_date = now,
                    stop_date = DateTime(3000, 1, 1)
    )
    assignment.open()
    user = person.newContent(
                    portal_type = "ERP5 Login",
                    default_reference = "scalability_user_%i" % i,
                    password = password,
    )
    user.validate()
  #context.createScalabilityTestUsersFile(user_number, password)
except Exception as e:
  status_code = 1
  error_message = str(e)

return {'status_code' : status_code, 'error_message': error_message, 'password' : password }
