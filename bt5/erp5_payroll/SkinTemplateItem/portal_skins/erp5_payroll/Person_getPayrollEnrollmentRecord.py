# Returns a payroll enrollment record specific to a working contract
# made between an employee and a company

portal = context.getObject()
organisation_module = portal.getDefaultModuleValue("Organisation")

def getObjectOrRaise(module, id):
  obj = getattr(module, id, None)
  if obj is None:
    raise AttributeError("%s doesn't have sub-object with id %s" % (module, id))
  else:
    return obj

# Try to get objects from id
if isinstance(organisation, str):
  organisation = getObjectOrRaise(organisation_module, organisation)

# If no id, let's expect that the parameters are objects
career_step_list = context.objectValues(portal_type="Career",
                                        subordination_uid=organisation.getUid(),
                                        validation_state='open')
if len(career_step_list) <= 0:
  raise ValueError("No open Career for employee %s" % context.getRelativeUrl())
else:
  # For the moment, only the case of 1 open Career step per Person 
  # and Organisation is taken into account
  career_step = career_step_list[0]

record = career_step.getAggregateValue()
if record is None:
  raise AttributeError("No Payroll Enrollment Record found for employee %s" % context.getRelativeUrl())

return record
