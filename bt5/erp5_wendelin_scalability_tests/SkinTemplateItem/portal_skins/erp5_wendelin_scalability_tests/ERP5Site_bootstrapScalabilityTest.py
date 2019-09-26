# Script that installs the configurator for scalabiility tests

import random
import string
import json

request = context.REQUEST
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

status_code = 0
error_message = "No error."

context.ERP5Site_setUpActivityTool()

if user_quantity is None: 
  return json.dumps({"status_code" : 1, 
                     "error_message": "Parameter 'user_quantity' is required.", 
                     "password" : None })

password = ''.join(random.choice(string.digits + string.letters) for i in xrange(10))

# check erp5_scalability_test business template is present
configurator = portal.business_configuration_module.default_wendelin_configuration
if configurator == None or not configurator.contentValues(portal_type='Configuration Save'):
  error_message = "Could not find the scalability business configuration object. Be sure to have erp5_scalability_test business template installed."
  return json.dumps({"status_code" : 1, 
                     "error_message": error_message })

# install configurator if not intalled
if configurator.getSimulationState() == "draft":
  person = portal_catalog.getResultValue(portal_type="Person", title = 'Scalability company')
  organisation = portal_catalog.getResultValue(portal_type="Organisation", title = 'Scalability company')
  if person is None or organisation is None:
    try:
      configurator.buildConfiguration()
    except Exception as e:
      status_code = 1
      error_message = "Error during installation: " + str(e)
      return json.dumps({"status_code" : 1, 
                         "error_message": error_message })

# create users if installation is done
try:
  context.portal_categories.activate(after_method_id = ('ERP5Site_afterConfigurationSetup',
                                     'immediateReindexObject')
                                     ).ERP5Site_createTestData(user_quantity, password)
  context.portal_categories.activate(after_method_id = ('ERP5Site_afterConfigurationSetup',
                                     'immediateReindexObject')
                                     ).ERP5Site_setIdGenerator()
except Exception as e:
  status_code = 1
  error_message = "Error calling ERP5Site_createTestData script: " + str(e)
  return json.dumps({"status_code" : 1, 
                     "error_message": error_message })

return json.dumps({"status_code" : status_code, 
                   "error_message": error_message, 
                   "password" : password, 
                   "quantity" : user_quantity })
