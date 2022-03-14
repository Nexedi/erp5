# Example code:

from past.builtins import cmp
def getCompactTitle(category):
  title_list = []
  while category.getPortalType() == 'Category':
    if category.getCodification() or category.getShortTitle():
      compact_title = category.getTranslatedShortTitle() or category.getReference() or category.getTranslatedTitle()
      title_list.append(compact_title)
    category = category.getParentValue()
  if title_list:
    title_list = title_list[:-1]
    title_list.reverse()
  return '/'.join(title_list)

def compareTitle(a, b):
  return cmp(a[1], b[1])

def getCompactChildItemList(context):
  result = context.getCategoryChildItemList(display_method=getCompactTitle)
  result.sort(compareTitle)
  return result

from Products.ERP5Type.Cache import CachingMethod
cached_getCompactChildItemList = CachingMethod(getCompactChildItemList, id='getCompactChildItemList')
return cached_getCompactChildItemList(context)
