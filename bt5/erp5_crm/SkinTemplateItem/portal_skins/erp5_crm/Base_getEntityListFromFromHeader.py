getResultValue = context.portal_catalog.getResultValue

from Products.ERP5Type.Utils import Email_parseAddressHeader

result = []
for _, recipient in Email_parseAddressHeader(text):
  if recipient:
    email = getResultValue(url_string={'query':recipient, 'key':'ExactMatch'}, portal_type='Email', parent_portal_type='Person')
    if email is None:
      email = getResultValue(url_string={'query':recipient, 'key':'ExactMatch'}, portal_type='Email', parent_portal_type='Organisation')
    if email is not None:
      result.append(email.getParentValue())
return result
