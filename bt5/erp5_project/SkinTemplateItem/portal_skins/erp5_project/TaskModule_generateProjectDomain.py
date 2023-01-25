restrictedTraverse = context.getPortalObject().restrictedTraverse
domain_list = []

def Task_getRelatedSourceProject(depth, parent_relative_url=None):
  if depth == 0:
    task_uid_list  = context.portal_selections.getSelectionUidList(context=context, selection_name='task_module_selection')
    project_result = context.portal_catalog(portal_type=["Project", "Project Line"],
                                            source_project_related_uid=task_uid_list,
                                            select_list=['portal_type', 'relative_url', 'id', 'title'],
                                            sort_on = (('title','ascending'),))
  else:
    project_result = context.portal_catalog(portal_type=["Project Line", "Project Milestones"],
                                            select_list=['portal_type', 'relative_url', 'id', 'title'],
                                            parent_relative_url=parent_relative_url,
                                            sort_on = (('title','ascending'),))
  # use a dict to store catalog result
  project_dict = {}
  category_dict = {}
  project_list = []
  append = project_list.append
  for x in project_result:
    key = x.uid
    if key not in project_dict:
      project_dict[key] = None
      category_dict = {'relative_url':x.relative_url,
                       'portal_type':x.portal_type,
                       'id':x.id,
                       'title':x.title,
                       'uid':x.uid}
      append(category_dict)

  return project_list

def Task_getRelatedSourceProjectCategory(depth):
  parent_relative_url = None
  if depth > 0:
    parent_relative_url = parent.getMembershipCriterionCategoryList()
  project_list = Task_getRelatedSourceProject(depth=depth,
                                              parent_relative_url=parent_relative_url)

  category_dict = {}
  category_list = []
  append = category_list.append

  for project in project_list:
    if project['portal_type'] == 'Project' or depth > 0:
      category = project
    else:
      # XXX here we need to get the project line object to get the explanation value
      project_line_value = restrictedTraverse(project['relative_url'])
      explanation_value = project_line_value.getExplanationValue()
      category = {'relative_url':explanation_value.getRelativeUrl(),
                  'portal_type':explanation_value.getPortalType(),
                  'id':explanation_value.getId(),
                  'title':explanation_value.getTitle(),
                  'uid':explanation_value.getUid()}
    key = category['uid']
    if key not in category_dict:
      category_dict[key] = None
      append(category)

  return category_list

category_list = Task_getRelatedSourceProjectCategory(depth)

for category in category_list:
  domain = parent.generateTempDomain(id = 'sub' + category['id'] )
  domain.edit(title = category['title'],
              membership_criterion_base_category = ('source_project', ),
              membership_criterion_category = (category['relative_url'],),
              domain_generator_method_id = script.id,
              uid = category['uid'])

  domain_list.append(domain)
return domain_list
