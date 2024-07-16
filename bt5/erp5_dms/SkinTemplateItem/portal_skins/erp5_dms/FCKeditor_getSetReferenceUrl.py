# use 'id' for embedded document, and use 'reference' for non-embedded document.
# XXX the condition should be changed when we introduce Embedded Image / File portal type.
if brain.getValidationState() == 'embedded':
  reference = brain.getId()
else:
  reference = brain.getReference()

import six
return six.text_type(
    "javascript:SelectFile('%s?format=%s')" % (
        reference.replace("'", "\\'"),
        context.getPortalObject().portal_preferences.getPreferredImageFormat()
    ),
    'utf-8',
)
