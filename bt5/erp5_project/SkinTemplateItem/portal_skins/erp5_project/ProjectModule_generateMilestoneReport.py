"""
This script is in charge to retrive all milestones that
match report parameters, then sort them and prepare data
that will allows to generate temp objects for listbox
"""
listbox = []
portal = context.getPortalObject()

sql_kw = {}
if project_validation_state_list is not None and \
    len(project_validation_state_list):
  sql_kw['validation_state'] = project_validation_state_list

project_list = portal.portal_catalog(portal_type='Project', **sql_kw)
project_uid_list = [x.uid for x in project_list]

sql_kw = {}

select_dict = {}
select_dict['title'] = None
select_dict['description'] = None
select_dict['parent_title'] = None
milestone_list = []
portal_catalog = portal.portal_catalog
# Check for some extra properties that are not necessarly
# in the catalog. We need by the way to check if
# hasColumn exists, it is new and is not installed yet everywhere
hasColumn = getattr(portal_catalog, 'hasColumn', None)
if hasColumn is not None:
  for prop in ['outcome_description']:
    if hasColumn(prop):
      select_dict[prop] = None

if len(project_uid_list):
  milestone_list = [x for x in portal.portal_catalog(parent_uid=project_uid_list,
                       portal_type='Project Milestone', select_dict=select_dict, **sql_kw)]

milestone_list.sort(key = lambda x: (x.parent_title, getattr(x, 'stop_date', None), x.title))

for milestone in milestone_list:
  # We wish to display the project only for the first milestone
  # of this project

  # XXX These two statements below filter the result,
  # we can increase speed by filtering directly from the database.
  if from_date is not None:
    if milestone.getStartDate() < from_date:
      continue
  if at_date is not None:
    if milestone.getStopDate() >= at_date:
      continue
  line_kw = {}
  line_kw['project_title'] = milestone.parent_title
  line_kw['milestone_title'] = milestone.title
  line_kw['stop_date'] = getattr(milestone, 'stop_date', None)
  line_kw['milestone_description'] = milestone.getProperty('description')
  line_kw['milestone_outcome_description'] = milestone.getProperty('outcome_description')
  listbox.append(line_kw)

context.Base_updateDialogForm(listbox=listbox, empty_line_number=0)
return context.ProjectModule_viewMilestoneReport()
