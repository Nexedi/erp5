## Script (Python) "Resource_getChartCurrentInventoryList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from DateTime import DateTime
result = map(lambda x:(x[0], x[1]), context.Resource_zGetChartInventoryList(to_date=DateTime(),resource_uid=context.getUid()))
result = filter(lambda x: x[1] > 0, result)
return result
