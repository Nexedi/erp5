result = []

for r in context.contentValues(portal_type= "Requirement", sort_on = (('int_index','ascending', 'int'),)):
  if not r.getRequirementRelatedValueList():
    if not r.contentValues(portal_type= "Requirement", sort_on = (('int_index','ascending', 'int'),)):
      result.append({'requirement_reference': r.Requirement_getDefaultReference(),
                     'requirement_title': r.getTitle(),
                     'project_reference': 'Not covered',
                     'project_title': '',
                     'stop_date': None})
  else:
    for p in r.getRequirementRelatedValueList():
      result.append({'requirement_reference': r.Requirement_getDefaultReference(),
                     'requirement_title': r.getTitle(),
                     'project_reference': p.Project_getDefaultReference(),
                     'project_title': p.getTitle(),
                     'stop_date': p.getStopDate()})
  result.extend(r.RequirementDocument_getProjectCoverageList())

return result
