## Script (Python) "ERP5Site_getModuleItemList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.ERP5Type.Cache import CachingMethod

try:
  user = context.portal_membership.getAuthenticatedMember().getUserName()
except:
  user = None

def getModuleItemList(user=None):
  translate = context.translation_service.translate

  item_list = []
  for module in context.getPortalObject().objectValues('ERP5 Folder'):
    url = module.absolute_url()
    label = module.getTitle() or module.getId()
    label = translate('ui', label)
    item_list.append((url, label))

  def compareModules(a, b): return cmp(a[1], b[1])
  item_list.sort(compareModules)
  return item_list

getModuleItemList = CachingMethod(getModuleItemList, id='ERP5Site_getModuleItemList')
return getModuleItemList(user=user)

