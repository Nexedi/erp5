"""Manager Proxy Role allows anonymous users to create events
"""
if REQUEST is not None:
  from zExceptions import Unauthorized
  portal = context.getPortalObject()
  raise Unauthorized(portal.Base_translateString('You are not allowed to call this script by your own'))
context.newContent(**kw)
