from builtins import str
project = context
reference_list = []

# return reference if defined:
reference = project.getReference()
if reference: return reference

# Set marker for milestone
project_item_type = project.getPortalType()

# browse projects parents until base found
# assemble list of default reference items
while project.getPortalType() in ( "Project Line", "Project Milestone"):
  reference = project.getReference()
  reference_list.append(reference or str(project.getProperty('int_index', '') or '') or project.getId())
  project = project.getParentValue()
  # Quick exit if some parent project defines a reference
  if reference:
    reference_list.reverse()
    return '-'.join(reference_list)

# Add M for milestone
if project_item_type == "Project Milestone":
  reference_list.append('M')

# Append default reference (P)
reference_list.append(reference or 'P')
reference_list.reverse()
return '-'.join(reference_list)
