## Script (Python) "Base_renameCategory"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=from_cat = None, to_cat = None
##title=
##
new_category_list = ()
from_cat = from_cat + '/'
to_cat = to_cat + '/'
has_changed = 0

if from_cat is not None and to_cat is not None:
  for o in context.objectValues():
    has_changed = 0
    new_category_list = ()
    for cat in o.getCategoryList():
      if cat.find(from_cat) == 0:
        cat = to_cat + cat[len(from_cat):]
        has_changed = 1
      new_category_list += (cat,)
    if has_changed == 1:
      o.setCategoryList(new_category_list)
      print "changed category %s with %s on %s" % (str(from_cat),str(to_cat),str(o.getPath()))


print " "
return printed
