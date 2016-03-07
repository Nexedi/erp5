result = []

for r in context.contentValues(portal_type= "Requirement", sort_on = (('int_index','ascending', 'int'),), checked_permission='View'):
  requirement_related_list = r.getRequirementRelatedValueList()
  requirement_related_count = len(requirement_related_list)
  if not requirement_related_list:
    if not r.contentValues(portal_type= "Requirement", sort_on = (('int_index','ascending', 'int'),), checked_permission='View'):
      result.append({'requirement_reference': r.Requirement_getDefaultReference(),
                     'requirement_title': r.getTitle(),
                     'requirement_comment': r.getComment(),
                     'repeat_index' : 0,
                     'repeat_count' : 1,
                     'project_reference': 'Not covered',
                     'project_title': '',
                     'stop_date': None})
  else:
    i = 0
    for p in requirement_related_list:
      result.append({'requirement_reference': r.Requirement_getDefaultReference(),
                     'requirement_title': r.getTitle(),
                     'requirement_comment': r.getComment(),
                     'repeat_index' : i,
                     'repeat_count' : requirement_related_count,
                     'project_reference': p.Project_getDefaultReference(),
                     'project_title': p.getTitle(),
                     'stop_date': p.getStopDate()})
      i += 1
  result.extend(r.RequirementDocument_getProjectCoverageList())

return result
