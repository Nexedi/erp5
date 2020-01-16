import os
import base64

# This is python 3.6 secret.token_urlsafe
random_id = base64.urlsafe_b64encode(os.urandom(48)).rstrip(b'=').decode('ascii')

# Define Reference from ID provided by portal_ids
portal = context.getPortalObject()
type_definition = context.getTypeInfo()

short_portal_type = type_definition.getShortTitle()
if not short_portal_type:
  short_portal_type = ''.join(s for s in type_definition.getId() if s.isupper())

id_group = ('reference', short_portal_type)
default = 1
new_id = portal.portal_ids.generateNewId(id_group=id_group, default=default)
reference = '%s-%s%s' % (short_portal_type, new_id, random_id)

context.setReference(reference)
