## Script (Python) "Account_getPcgItemList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
def display(x):
  return "%s - %s" % (x.getId(), x.getTitle())

def sort(x,y):
  return cmp(display(x), display(y))

obj = context.restrictedTraverse('portal_categories/pcg')
item_list = obj.getCategoryChildItemList(base=0, display_method=display, sort_method=sort)
return item_list
