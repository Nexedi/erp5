result = ''# '---<br>'
i = 0
for brain in context.getPortalObject().portal_catalog(portal_type='Action Information', sort_on=[['relative_url', 'ASC']]):
  action = brain.getObject()
  action_type = action.getActionType()
  if not action.isVisible():
    continue
  if ('Template' in action.getParentTitle()):
    continue
  if (action_type in ['object_button']):
    continue
  # if (action_type in ['object_report', 'object_exchange']):
  #   continue
  if ('web' in action_type) or ('jio' in action_type) or (action_type in ['object_view', 'object_list', 'object_jump', 'object_sort', 'object_ui', 'object_search']):
    continue

  i += 1
  result += '%s %s %s %s' % (action.getParentTitle(), '<a href="%s">%s</a>' % (action.getRelativeUrl(), action.getTitle()), action.getActionType(), '<br>')

result = '--- %i<br>%s' % (i, result)
print result
return printed

# check selection content
portal = context.getPortalObject()
print '---'
for selection_id in ('bar_selection', 'foo_selection'):
  print selection_id
  params = portal.portal_selections.getSelectionParamsFor(selection_id)
  print '%s' % str(params)
  print portal.portal_selections.getSelectionColumns(selection_id)

print 'ok'
return printed

# delete all persons
context.portal_catalog.searchAndActivate(
  portal_type='Person',
  parent_uid=context.getUid(),
  method_id='Couscous_deleteIfExpectedId'
)
return 'ok'


context.getPortalObject().notebook_module.olapy_notebook.edit(title="olapy_notebook.jsmd", reference="olapy_notebook.jsmd")
return "ok"

import time
time.sleep(360)
return 'cosucous'


portal_object = portal = context.getPortalObject()
module = portal.person_module

i = 0
while i < 80000:
  module.newContent(portal_type='Person', title='test %i' % i)
  i += 1

return 'couscous'


return 'ok'

from DateTime import DateTime
portal = context.getPortalObject()

token = portal.access_token_module.newContent(
  id='%s-%s' % (DateTime().strftime('%Y%m%d'), portal.Base_generateAccessTokenHalID()),
  portal_type='HAL Access Token',
  agent='person_module/160295'
)
token.validate()
return token.getRelativeUrl()







from DateTime import DateTime
i = 0
while i < 700:
  context.newContent(
    portal_type='Test Result Line',
    string_index=i,
    title=i,
    start_date=DateTime(),
    duration=i,
    all_tests=i,
    errors=1,
    failures=2,
    skip=3,
  )
  i += 1
return 'ok'





context.portal_catalog.searchAndActivate(
  portal_type='Person',
  parent_uid=context.getUid(),
  method_id='testromain2'
)
return 'ok'








context.portal_catalog.searchAndActivate(
  portal_type='Person',
  parent_uid=context.getUid(),
  method_id='testromain2'
)
return 'ok'



return 'ok'




# python: here.Module_listWorkflowTransitionItemList()['form_id_dict'].get(request.get("field_your_mass_workflow_action", ""), '')

result = None
form_id_dict = context.Module_listWorkflowTransitionItemList()['form_id_dict']

# During rendering, this variable has been set into the request
# Render what user selected
action = request.get("mass_workflow_action", "")
if action:
  return form_id_dict.get(action, '')

# Validate only if user didn't change the possible action
action = request.get("field_your_mass_workflow_action", "")
if (action and action == request.get("field_your_previous_mass_workflow_action", "")):
  return form_id_dict.get(action, '')

return ''

portal_object = portal = context.getPortalObject()
module = portal.foo_module

i = 0
while i < 80000:
  module.newContent(portal_type='Foo', title='test %i' % i)
  i += 1

return 'couscous'


raise NotImplementedError(context.REQUEST)

return '%s %s %s %s' % (portal.portal_url(), portal.absolute_url(), portal.absolute_url_path(), context.REQUEST.physicalPathToURL(portal.getPhysicalPath() + ("",)))


return portal_object.portal_preferences.getPreference('preferred_foo_use', None)

domain_tool = portal_object.portal_domains
base_domain = domain_tool.foo_domain
url_domain = portal_object.portal_url

def generateRecur(domain, depth, result_list):
  if depth:
    result_list.append(('/'.join(url_domain.getRelativeContentPath(domain)[2:]), domain.getTitle()))
  new_depth = depth + 1
  for sub_domain in domain_tool.getChildDomainValueList(domain, depth=depth):
    generateRecur(sub_domain, new_depth, result_list)

value_list = []
generateRecur(base_domain, 0, value_list)
print value_list

value_list = []
print value_list

return printed


def getDomainSelection(domain_list):
  root_dict = {}

  if len(domain_list) > 0:
    category_tool = portal.portal_categories
    domain_tool = portal.portal_domains
    preference_tool = portal.portal_preferences

  for base_domain_id in domain_list:
    domain = None
    if category_tool is not None:
      domain = category_tool.restrictedTraverse(base_domain_id, None)
      if domain is not None :

        root_dict[base_domain_id] = getattr(
          domain,
          preference_tool.getPreference(
            'preferred_category_child_item_list_method_id',
            'getCategoryChildCompactLogicalPathItemList'
          )
        )(local_sort_id=('int_index', 'translated_title'), checked_permission='View',
          filter_node=0, display_none_category=0)

      elif domain_tool is not None:
        try:
          domain = domain_tool.getDomainByPath(base_domain_id, None)
        except KeyError:
          domain = None
        if domain is not None:
          # XXX Implement recursive fetch
          root_dict[base_domain_id] = [(x.getTitle(), x.getId()) for x in domain_tool.getChildDomainValueList(domain, depth=0)]

  return root_dict



return getDomainSelection(['foo_domain'])













return portal_object.portal_catalog(selection_domain={'region': 'france'}, src__=1)

return portal_object.portal_catalog(selection_domain={'region': portal_object.portal_categories.region.france}, src__=1)

domain = portal_object.portal_domains.getDomainByPath('validated_project_domain')
sql_catalog = portal_object.portal_catalog.getSQLCatalog()

return portal_object.portal_catalog(src__=1, full_text='title:"nutnut" AND validated_project_domain:"sub1" AND selection_domain:"region:france"')

query_kw = dict(selection_domain={
                    'validated_project_domain': domain.getChildDomainValueList(domain, depth=0)[0],
                    'region': portal_object.portal_categories.region.france
                })

return sql_catalog.buildQuery(query_kw).asSearchTextExpression(sql_catalog)
return portal_object.portal_catalog(src__=1, **query_kw)

return portal_object.portal_catalog(selection_domain={'region': portal_object.portal_categories.region.france}, src__=1)



from Products.ERP5Form.Selection import Selection, DomainSelection

def getDomainSelection(self, domain_list):
  """Return a DomainSelection object wrapped with the context.
  """
  portal_object = self.getPortalObject()
  root_dict = {}

  if len(domain_list) > 0:
    category_tool = portal_object.portal_categories
    domain_tool = portal_object.portal_domains
    preference_tool = portal_object.portal_preferences

    for domain in domain_list:

      root = None
      base_domain = domain.split('/', 1)[0]
      if category_tool is not None:
        root = category_tool.restrictedTraverse(domain, None)
        if root is not None :

          root_dict[base_domain] = getattr(
            root,
            preference_tool.getPreference(
              'preferred_category_child_item_list_method_id',
              'getCategoryChildCompactLogicalPathItemList'
            )
          )(local_sort_id=('int_index', 'translated_title'), checked_permission='View',
            filter_node=0, display_none_category=0)

        elif domain_tool is not None:
          try:
            root = domain_tool.getDomainByPath(domain, None)
          except KeyError:
            root = None
          if root is not None:
            root_dict[base_domain] = [(x.getTitle(), x.getId()) for x in root.getChildDomainValueList(root, depth=0)]
      if root is None:
        root = portal_object.restrictedTraverse(domain, None)
        if root is not None:
          root_dict[None] = (None, domain)

    return root_dict
    # return DomainSelection(domain_dict = root_dict)#.__of__(self.getContext())

return getDomainSelection(context, ['parent', 'region', 'validated_project_domain', 'preferred_group_person_list_domain', 'ledger'])#.asDomainItemDict(portal=context.getPortalObject())


return context.getPortalObject().TaskModule_viewTaskList.listbox.getDomainSelection()


# from Products.ERP5Form.Tool.SelectionTool import makeTreeList
# return makeTreeList()

# return context.getPortalObject().portal_selections.

return context.getPortalObject().portal_catalog(selection_domain={'group': context}, src__=1)

return "couscous"

context.setContentType(None)
context.edit(content_type=None)
# delete content.content_type
return "ok"
# Example code:

# Import a standard function, and get the HTML request and response objects.
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
response =  request.response

# Return a string identifying this script.
print "This is the", script.meta_type, '"%s"' % script.getId(),
if script.title:
    print "(%s)" % html_quote(script.title),
print "in", container.absolute_url()
return printed
