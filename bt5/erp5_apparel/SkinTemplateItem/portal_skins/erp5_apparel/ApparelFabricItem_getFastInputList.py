# erp5_apparel/ApparelFabricItem_getFastInputList

from builtins import str
from builtins import range
from Products.ERP5Type.Document import newTempBase

object_list = []
for i in range(0,10):
  line = newTempBase(context, 'tmp_install_%s' %(str(i)))
  line.edit(title = 'title_%s' %str(i), quantity="")
  line.setUid('new_%s' % i)
  object_list.append(line)

return object_list
