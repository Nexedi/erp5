# Get the objects based on domain used

selection_tool = context.portal_selections
selection = selection_tool.getSelectionFor('project_planning_selection')

if selection is not None:
  if selection.report_path in ('task_module_domain', 'project_person_domain'):
    kw['source_project_relative_url'] = (context.getRelativeUrl(), '%s/%%' % context.getRelativeUrl())
  elif selection.report_path == 'project_person_task_report_domain':
    # It was required filter to one specific portal type
    kw['portal_type'] = ['Task Report']
    kw['source_project_relative_url'] = (context.getRelativeUrl(), '%s/%%' % context.getRelativeUrl())
  elif selection.report_path == 'project_projectline_domain':
    kw['source_project_relative_url'] = (context.getRelativeUrl(), '%s/%%' % context.getRelativeUrl())
  elif selection.report_path in ('task_report_module_domain', 'project_project_task_report_domain'):
    # It was required filter to one specific portal type
    kw['portal_type'] = ['Task Report']
    kw['source_project_relative_url'] = (context.getRelativeUrl(), '%s/%%' % context.getRelativeUrl())
  elif selection.report_path == 'parent':
    return context.searchFolder(**kw)
  else:
    raise NotImplementedError("Unknow domain %s" % selection.report_path)

  return context.portal_catalog(**kw)

else:
  return context.searchFolder(**kw)
