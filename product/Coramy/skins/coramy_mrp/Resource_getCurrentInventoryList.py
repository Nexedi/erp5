## Script (Python) "Resource_getCurrentInventoryList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
from DateTime import DateTime
return context.Resource_zGetInventoryList(resource_uid = context.getUid(), to_date = DateTime(), **kw)
