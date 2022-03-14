from builtins import range
from collections import OrderedDict
from json import dumps
label_list = context.getLabelValueList()
num = len(label_list)
result_list = []
for line in context.query():
  value_list = line.getValueList()
  result_list.append(OrderedDict([(label_list[i][1], value_list[i][0]) for i in range(num)]))
return dumps(OrderedDict([('title',context.getTitle()), ('data',result_list)]))
