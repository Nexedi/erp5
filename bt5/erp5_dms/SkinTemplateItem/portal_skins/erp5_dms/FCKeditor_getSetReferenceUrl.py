# use 'id' for embedded document, and use 'reference' for non-embedded document.
# XXX the condition should be changed when we introduce Embedded Image / File portal type.
from builtins import str
if brain.getValidationState() == 'embedded':
  reference = brain.getId()
else:
  reference = brain.getReference()

return str(
    "javascript:SelectFile('%s?format=%s')" % (
        reference.replace("'", "\\'"),
        context.getPortalObject().portal_preferences.getPreferredImageFormat()
    ),
    'utf-8',
)
