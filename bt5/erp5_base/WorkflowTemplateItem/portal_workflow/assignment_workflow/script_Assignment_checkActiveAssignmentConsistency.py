# XXX
# This script is given as a possible example of consistency checking.
# So for now, it is not called by any transition, but if you want to use it,
# please use it in the "Script (before)" of the "open_action" transition.
# In this case we want to be sure that open assignments share the same site category.
# XXX

from Products.ERP5Type.Core.Workflow import ValidationFailed

# Get the assignment object and its parent
assignment_object = state_change['object']
person_object     = assignment_object.getParentValue()

# Add the current assignment site
assignment_site_list = [assignment_object.getSite()]

# Get the list of site property from open assignments
for assignment in person_object.contentValues(filter={'portal_type': 'Assignment'}):
  if assignment.getValidationState() == 'open':
    assignment_site = assignment.getSite()
    if assignment_site not in assignment_site_list:
      assignment_site_list.append(assignment_site)

# The only case when several assignments can be started at the same time is when they share the same 'site' value.
if len(assignment_site_list) != 1:
  raise ValidationFailed("Error: started assignments must have the same site value.")
