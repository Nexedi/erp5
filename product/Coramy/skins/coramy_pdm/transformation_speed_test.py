## Script (Python) "transformation_speed_test"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Example code:
print "<html><p>Begin</p>"

transformation_list = [context] + context.getSpecialiseValueList()
#print "%s<br>" % context.getValueList('specialise', portal_type=())
#print "%s<br>" % context.getCategoryMembershipList('specialise', portal_type=())
#print "%s<br>" % context.portal_categories.restrictedTraverse('transformation/70170').id
print "%s<br>" % map(lambda x: x.id, transformation_list )

for transformation in transformation_list:
  for t in transformation.objectValues():
    r = t.getResourceDefaultValue()
    print '-%s %s<br>' % (t.id, r.getBasePrice())
    for c in t.objectValues():
      print ' +%s<br>' % c.id 

print "<p>End</p></html>"

return printed
