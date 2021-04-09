"""
  Create a zuite or return an existing one after remove his contents.
"""
from zExceptions import BadRequest
assert context.getPortalType() == "Test Tool", "bad context"
if REQUEST:
  raise RuntimeError("You can not call this script from the URL")

if zuite_id is None:
  raise ValueError("Zuite_id cannot be None!")

if zuite_id not in context.objectIds():
  factory = context.portal_tests.manage_addProduct['Zelenium']
  factory.manage_addZuite(id=zuite_id)

zuite = getattr(context.portal_tests, zuite_id)
if zuite.getMetaType() != "ERP5 Test Tool":
  raise ValueError("Zuite is not a ERP5 Test Tool")

try:
  zuite.manage_delObjects(zuite.objectIds())
except BadRequest:
  pass
return zuite
