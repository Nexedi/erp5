portal = context.getPortalObject()
current_object = context.getObject()
context.log(current_object)
context.log(current_object.getDestinationRelatedValueList())
person_list = [assignment.getParentValue() for assignment in current_object.getDestinationFormRelatedValueList()]
return person_list
