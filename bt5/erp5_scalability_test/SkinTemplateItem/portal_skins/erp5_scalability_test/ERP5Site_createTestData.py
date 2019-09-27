# Script that creates "user_quantity" users for scalabiility tests:
# creates and validates persons
# adds assignment and starts it
# creates user (login credentials)
# random password is given by parameter
from DateTime import DateTime
import json
now = DateTime()

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

try:
  organisation = portal_catalog.getResultValue(
                    portal_type="Organisation",
                    title = 'Scalability company')
  if organisation is None:
    error_message = "Could not find the scalability organisation. Standard configuration not installed?"
    return json.dumps({"status_code" : 1, "error_message": error_message, "password" : None })
  organisation = organisation.getObject().getRelativeUrl()

  for i in xrange(0, int(user_quantity)):
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

    assignment_id_list = [x.getId() for x in person.objectValues(portal_type="Assignment")]
    if assignment_id_list: person.manage_delObjects(ids=assignment_id_list)
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

    user_id_list = [x.getId() for x in person.objectValues(portal_type="ERP5 Login")]
    if user_id_list: person.manage_delObjects(ids=user_id_list)
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
  raise e
