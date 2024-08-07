"""
  Return true or false based on if document is convertible or not.
"""
MARKER = (None, b'',)
portal = context.getPortalObject()

portal_type = context.getPortalType()
allowed_portal_type_list = portal.getPortalDocumentTypeList() + portal.getPortalEmbeddedDocumentTypeList()

if portal_type not in allowed_portal_type_list:
  return False

# XXX hardcoded validation states blacklist. Do State Types?
if context.getValidationState() in ["draft", "deleted", "cancelled", "archived"]:
  return False

# XXX: we do check if "data" methods exists on pretending to be Document portal types
# we need a way to do this by introspection
return (getattr(context, "getData", None) is not None and context.getData() not in MARKER) or \
       (getattr(context, "getBaseData", None) is not None and context.getBaseData() not in MARKER)
