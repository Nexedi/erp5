## Script (Python) "Resource_getInventoryList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
return context.Resource_zGetInventoryList(resource_uid = context.getUid(), **kw)
