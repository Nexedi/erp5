## Script (Python) "Delivery_getInventoryList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
from DateTime import DateTime
resource_uid_list = map(lambda o:o.getResourceUid(),context.contentValues(filter={'portal_type': context.getMovementTypeList()}))
return context.Delivery_zGetInventoryList(to_date=DateTime(),resource_uid_list=resource_uid_list, **kw)
