"""Returns all validated projects.

This script is indented to be used on custom listfields for accounting lines, and on reports.
If this script returns an empty list, it means that reports by project are disabled.
"""
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

# case 1: script is used for reports, we display all validated projects.
if context.getPortalType() == 'Accounting Transaction Module':
  project_list = []
  for project in portal.portal_catalog(
                           portal_type='Project',
                           select_list=['relative_url', 'title', 'reference'],
                           validation_state=('validated',),
                           sort_on=(('title', 'ASC'),)):
    if project.reference:
      project_list.append(('%s - %s' % (project.reference, project.title), project.relative_url,))
    else:
      project_list.append((project.title, project.relative_url,))

  if not project_list:
    return [] # returning an empty list, not to add project column on reports
  return [('', ''), (str(translateString('No Project')), 'None')] + project_list

# case 2: script is used on custom listfields.
#  for now the script has to be customized in such case.
# [(x.getTitle(), x.getRelativeUrl()) for x in context.project_module.searchFolder()]
return [('', '')]
