""" This script is used initially by PlanningBox tests currently"""
from builtins import str
for i in context.objectValues():
  i.setStartDate(DateTime(DateTime().strftime("%Y/%m/%d"))+0.4)
  i.setStopDate(DateTime(DateTime().strftime("%Y/%m/%d"))+0.8)
  i.newContent(id = str(0), title = 'Title 4', portal_type='Foo Line' )
  i.setFooCategory('foo_category/a')

return 'Modified Successfully.'
