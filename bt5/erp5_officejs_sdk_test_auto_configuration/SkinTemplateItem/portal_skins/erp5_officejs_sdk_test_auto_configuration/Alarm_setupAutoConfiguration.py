"""
This script will setup the default OfficeJS SDK's configuration as saved in erp5_wendelin_scalability_test business template.
As this modifies your site care must be taken!
"""
from Products.ERP5Type.Log import log

portal = context.getPortalObject()
configurator = getattr(portal.business_configuration_module, "officejs_development_configuration_workflow", None)

if configurator == None:
  log("Could not find the scalability business configuration object. Be sure to have erp5_configurator_officejs_development business template installed.")
  return

# install configurator if not intalled
if not portal.ERP5Site_isReady():
  # nothing installed, thus do it
  log("START auto-configuration for OfficeJS SDK's default configuration.")
  context.ERP5Site_bootstrapScalabilityTest(user_quantity=0, setup_activity_tool=False, create_test_data=False, set_id_generator=False)
else:
  log("All configured. Nothing to do.")
