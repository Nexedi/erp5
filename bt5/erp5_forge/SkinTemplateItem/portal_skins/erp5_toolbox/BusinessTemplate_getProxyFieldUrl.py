from Products.PythonScripts.standard import html_quote

key = brain.object_id

portal_absolute_url = context.getPortalObject().absolute_url()

if brain.choice == '1_create_form':
  return None
else:
  return html_quote('%s/portal_skins/%s/manage_main' % (portal_absolute_url, key))
