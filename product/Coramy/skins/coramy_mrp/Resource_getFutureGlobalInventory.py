## Script (Python) "Resource_getFutureGlobalInventory"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=section_uid=None, **kw
##title=
##
from DateTime import DateTime
return context.Resource_zGetGlobalInventoryList(resource_uid = context.getUid(),  metanode="group/coramy", **kw)[0].inventory
