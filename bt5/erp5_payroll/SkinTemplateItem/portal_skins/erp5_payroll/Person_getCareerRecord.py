# Returns a payroll enrollment record specific to a working contract
# made between an employee and a company

portal = context.getObject()
organisation_module = portal.getDefaultModuleValue("Organisation")

def getObjectOrRaise(module, object_id):
  obj = getattr(module, object_id, None)
  if obj is None:
    raise AttributeError("%s doesn't have sub-object with id %s" % (module, object_id))
  else:
    return obj

# Try to get objects from id
if isinstance(organisation, str):
  organisation = getObjectOrRaise(organisation_module, organisation)

# If no id, let's expect that the parameters are objects
career_step_list = context.objectValues(portal_type="Career")
career_step_list = [career for career in career_step_list if career.getValidationState() == 'open']

if len(career_step_list) <= 0:
  raise ValueError("No open Career for employee %s" % context.getRelativeUrl())
else:
  # For the moment, only the case of 1 open Career step per Person 
  # and Organisation is taken into account
  career_step = career_step_list[0]

record = career_step.getAggregateValue(portal_type=portal_type)
if record is None:
  raise AttributeError("No %s found for employee %s" % (portal_type, context.getRelativeUrl()))

return record
