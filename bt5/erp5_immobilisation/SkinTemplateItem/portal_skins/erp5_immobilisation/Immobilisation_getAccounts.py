from past.builtins import cmp
from Products.ERP5Type.Cache import CachingMethod

def display(x):
  try:
    pcg_id = x.getGap().split('/')[-1]
  except:
    pcg_id = None
  account_title = x.getTitle()
  display = "%s - %s" % (pcg_id, account_title)
  return display

def sort_method(x, y):
  return cmp(x[0], y[0])

def getList():
  list = [(display(o), 'account_module/%s' % o.getId()) for o in context.account_module.objectValues()]
  list.sort(sort_method)
  return list


getList = CachingMethod(getList, 'getList')
return [('','')] + getList()
