portal = context.getPortalObject()

bt_repository_list = ['http://www.erp5.org/dists/snapshot/bt5/']
customer_user1_reference = 'PERSON_USER_REFERENCE'
customer_user1_used_reference = 'PERSON_RESERVED_REFERENCE'

# setup preferences
preference_id = 'default_initial_configurator_system_preference'

default_site_preference = getattr(portal.portal_preferences, preference_id, None)

if default_site_preference is None:
  default_site_preference = portal.portal_preferences.newContent(
                                id = 'default_initial_configurator_system_preference',
                                portal_type='System Preference', priority = 1)

default_site_preference.setPreferredHtmlStyleUnsavedFormWarning(False)
default_site_preference.setPreferredHtmlStyleDevelopperMode(None)
default_site_preference.setPreferredHtmlStyleAccessTab('1')

previous_conversion_server_url = portal.portal_preferences.getPreferredDocumentConversionServerUrl()
default_site_preference.setPreferredDocumentConversionServerUrl(previous_conversion_server_url)

if default_site_preference.getPreferenceState() != 'global':
  default_site_preference.enable()

# (Re)Create the Business Configurator
bc_id = 'STANDARD_CONFIGURATOR_TEST'
business_configuration = getattr(context.business_configuration_module, bc_id, None)
if business_configuration is not None:
  context.business_configuration_module.manage_delObjects([bc_id])

business_configuration = context.business_configuration_module.newContent(
                            portal_type="Business Configuration",
                            id=bc_id,
                            title=bc_id)

business_configuration.setResource(workflow_path)

# (Re)Create the Person and its ERP5 Login used to check that for user login
# (ERP5 Login.reference) unicity
kw = dict(portal_type="ERP5 Login",
          reference=customer_user1_used_reference)
erp5_login = context.portal_catalog.getResultValue(**kw)
if erp5_login is None:
  erp5_login = context.person_module.newContent(portal_type='Person').newContent(**kw)
if erp5_login.getValidationState() != 'validated':
  erp5_login.validate()

kw['reference'] = customer_user1_reference
person = context.portal_catalog.getResultValue(**kw)
if person is not None:
  context.person_module.manage_delObjects([person.getId()])

portal.portal_caches.clearAllCache()
return "### Init Ok ###"
