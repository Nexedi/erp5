# Script that installs the configurator for scalabiility tests:

import time

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

status_code = 0
error_message = "No error."

configurator = portal_catalog.getResultValue(
                  portal_type = "Business Configuration",
                  id = "default_standard_configuration",
                  title = "Small And Medium Business")

if configurator == None or not configurator.contentValues(portal_type='Configuration Save'):
  error_message = "Could not find the scalability business configuration object. Be sure to have erp5_scalability_test business template installed."
  return {'status_code' : 1, 'error_message': error_message }

try:
  configurator.buildConfiguration()
  # wait 15 minutes while configurator is installed
  time.sleep(15*60)
except Exception as e:
  status_code = 1
  error_message = "Error during installation: " + str(e)

return {'status_code' : status_code, 'error_message': error_message }
