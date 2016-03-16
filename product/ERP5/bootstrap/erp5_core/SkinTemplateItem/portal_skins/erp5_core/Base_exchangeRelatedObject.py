# this script is intended to repair errors.
# Let's say you use 2 objects, but this is the same one duplicated.
# So you want to keep only one object, so you have to remove
# all links to this old object and set the link on the new object.
from_object = context.organisation['314']
to_object = context.person['121']

from_object_related_object_list = context.portal_categories.getRelatedValueList(from_object)
for object in from_object_related_object_list:
  print object.getDestinationSection()
  object.setDestinationSectionValue(to_object)
  object.recursiveImmediateReindexObject()
return printed
