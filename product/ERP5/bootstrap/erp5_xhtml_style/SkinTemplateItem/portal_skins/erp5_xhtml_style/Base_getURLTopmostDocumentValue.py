"""
  this method is designed to get the topmost traversed url in an ERP5
  instance. By default it returns the portal. Overload this script if
  the portal is not the topmost traversed document in your setup.
"""
return context.getPortalObject()
