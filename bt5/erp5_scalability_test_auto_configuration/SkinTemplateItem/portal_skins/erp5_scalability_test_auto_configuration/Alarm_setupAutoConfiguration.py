"""
This script will setup the default ERP5's configuration as saved in erp5_scalability_test business template.
As this modifies your site care must be taken!
"""
from Products.ERP5Type.Log import log

portal = context.getPortalObject()
configurator = getattr(portal.business_configuration_module, "default_standard_configuration", None)

if configurator is None:
  log("Could not find the scalability business configuration object. Be sure to have erp5_scalability_test business template installed.")
  return

if not portal.ERP5Site_isReady():
  # nothing installed, thus do it
  log("START auto-configuration for ERP5's default configuration.")
  context.ERP5Site_bootstrapScalabilityTest(user_quantity=0, setup_activity_tool=False, create_test_data=False, set_id_generator=False)
else:
  log("All configured. Nothing to do.")
