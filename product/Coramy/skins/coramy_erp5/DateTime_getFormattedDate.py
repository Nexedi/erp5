## Script (Python) "DateTime_getFormattedDate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=date_time=None
##title=
##
from DateTime import DateTime

if date_time == None :
  date_time = DateTime()

return "%2.2d/%2.2d/%s" % (date_time.day(), date_time.month(), date_time.year())
