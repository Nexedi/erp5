# Browses the Integration Sites and calls the synchronize method's on each
for site in context.portal_integrations.objectValues():
  site.IntegrationSite_synchronize()

translateString = context.Base_translateString

portal_status_message = translateString("Synchronization started.")
context.Base_redirect(form_id, keep_items = dict(portal_status_message=portal_status_message))
