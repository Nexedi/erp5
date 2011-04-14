# Simple, stupid backward compatibility with existing persistent instances.
# Makes it possible to upgrade erp5_core on old sites (otherwise, saving to
# portal_trash fails).
from Products.ERP5Type.XMLObject import XMLObject as SQLCache

