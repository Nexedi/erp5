"""
  Currently it is not possible to change it to checkConsistency.
  If it added similar constraints at Documents will break archive
  behaviour.
"""
form_data = context.REQUEST.form
translateString =  context.Base_translateString

if clone:
  portal_type = context.getPortalType()
else:
  portal_type = form_data['clone_portal_type']

# prepare query params
kw = {'portal_type' : portal_type}
kw['reference'] = form_data.get('clone_reference') or ''
kw['version'] = form_data.get('clone_version') or ''
kw['language'] = form_data.get('clone_language') or ''

# Count documents of same reference and prepare kw
count = int(context.portal_catalog.countResults(**kw)[0][0])

if count:
  return translateString("Sorry, a ${portal_type} with reference '${reference}' and version '${version} [${language}]' already exists. Please select another reference or version.", mapping = kw)

return None
