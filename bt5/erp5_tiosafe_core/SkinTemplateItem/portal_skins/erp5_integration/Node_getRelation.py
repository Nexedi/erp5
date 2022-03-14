from builtins import str
sub = context.restrictedTraverse(context_document)
while sub.getParentValue().getPortalType() !=  "Synchronization Tool":
  sub = sub.getParentValue()

im = sub.Base_getRelatedObjectList(portal_type='Integration Module')[0].getObject()
org_module = im.getParentValue().organisation_module
org_pub = org_module.getSourceSectionValue()
gid = org_pub.getGidFromObject(context.getSubordinationValue(), encoded=False)

return str(gid)
