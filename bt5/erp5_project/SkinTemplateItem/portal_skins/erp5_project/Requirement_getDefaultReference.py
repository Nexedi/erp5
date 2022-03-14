from builtins import str
requirement = context
reference_list = []

# return reference if defined:
reference = requirement.getReference()
if reference: return reference

# browse requirements parents until base found
# assemble list of default reference items
while requirement.getPortalType() == "Requirement":
  reference = requirement.getReference()
  reference_list.append(reference or str(requirement.getProperty('int_index', '') or '') or requirement.getId())
  requirement = requirement.getParentValue()
  # Quick exit if some parent requirement defines a reference
  if reference:
    reference_list.reverse()
    return '-'.join(reference_list)

# Append default reference (R)
reference_list.append(reference or 'R')
reference_list.reverse()
return '-'.join(reference_list)
