project_count = 100
thread_per_project_count = 100
post_per_thread_amount = 97
max_new_document = 100

tag = 'POPULATE_FORUM'
after_tag = tag + 'XXX'


if (current_project_uid is None):
  if (created_project_count < project_count):
    created_project_count += 1
    created_thread_count = 0
    created_post_count = 0
    # no project, create
    project = context.project_module.newContent(
      portal_type='Project',
      title='Forum project %i' % created_project_count,
      activate_kw={'tag': tag}
    )
    return context.activate(after_tag=after_tag).testromain(
      current_project_uid=project.getUid(),
      created_project_count=created_project_count
    )
  else:
    return 'stopping'

if (current_thread_path is None):
  if (created_thread_count < thread_per_project_count):
    created_thread_count += 1
    thread = context.discussion_thread_module.newContent(
      portal_type='Discussion Thread',
      title='New Forum project %i discussion %i' % (created_project_count, created_thread_count),
      follow_up_uid=current_project_uid,
      activate_kw={'tag': tag}
    )
    thread.share()
    return context.activate(after_tag=after_tag).testromain(
      current_project_uid=current_project_uid,
      current_thread_path=thread.getRelativeUrl(),
      created_project_count=created_project_count,
      created_thread_count=created_thread_count
    )
  else:
    return context.activate(after_tag=after_tag).testromain(
      created_project_count=created_project_count
    )

if (current_thread_path is not None):
  if (created_post_count < post_per_thread_amount):
    for i in range(max_new_document):
      created_post_count += 1
      thread = context.restrictedTraverse(current_thread_path)
      post = thread.newContent(
        portal_type='Discussion Post',
        text_content="<p>Post %i</p><pre><code>def couscous:\n  return getTructruc()</code></pre><a href='https://www.nexedi.com'>Nexedi</a><img src='https://www.nexedi.com/img/nexedi-logo.png'></img><p>👍</p>" % created_post_count,
        activate_kw={'tag': tag}
      )
      # post.share()
    return context.activate(after_tag=after_tag).testromain(
      current_project_uid=current_project_uid,
      current_thread_path=current_thread_path,
      created_project_count=created_project_count,
      created_thread_count=created_thread_count,
      created_post_count=created_post_count
    )
  else:
    return context.activate(after_tag=after_tag).testromain(
      current_project_uid=current_project_uid,
      created_project_count=created_project_count,
      created_thread_count=created_thread_count
    )

return "ok"


context.setTitle("Prénom".decode("utf-8").encode("iso-8859-1"))
return "ok"

from AccessControl import getSecurityManager
from pprint import pformat
# vgetattr = context.test_vincent_getattr
user = getSecurityManager().getUser()
print 'User    :', repr(user)
# print '__dict__:', vgetattr(user, '__dict__')
print 'Id      :', repr(user.getId())
print 'Name    :', repr(user.getUserName())
print 'Roles   :', repr(user.getRoles())
print 'Groups  :', repr(getattr(user, 'getGroups', lambda: None)())
print 'Document:', repr(user.getUserValue())
print 'Login   :', repr(user.getLoginValue())
"""
print 'Properties:', pformat({
  x: user.getPropertysheet(x).propertyItems()
  for x in getattr(user, 'listPropertysheets', lambda: ())()
})
"""
return printed

from DateTime import DateTime
context.edit(start_date=DateTime())
return "ok"

sql_catalog = context.getPortalObject().portal_catalog.getSQLCatalog()

invalid_column_list = []
def isValidColumnOrRaise(column_id):
  is_valid_column = sql_catalog.isValidColumn(column_id)
  if not is_valid_column:
    invalid_column_list.append(column_id)
  return is_valid_column

result = sql_catalog.parseSearchText(
  'couscous AND taboulet AND a:"b" AND title:"couscous" AND lalala',
  search_key='FullTextKey',
  # is_valid=lambda x: False)
  is_valid=isValidColumnOrRaise)

return str(invalid_column_list)

# return context.portal_catalog(search_text='couscous AND taboulet AND a:"b" AND title:"couscous"', src__=1)
return context.portal_catalog(full_text='couscous AND taboulet AND a:"b" AND title:"couscous"', src__=1)

portal = context.getPortalObject()
bug_module = portal.task_module
for i in range(10000):
  task = bug_module.newContent(
    portal_type='Task',
    source_project='project_module/1'
  )
  task.newContent(portal_type='Task Line')
  task.newContent(portal_type='Task Line')

return 'ok'

result = ''# '---<br>'
i = 0
for brain in context.getPortalObject().portal_catalog(
  portal_type='Action Information',
  sort_on=[['relative_url', 'ASC']]
):
  action = brain.getObject()
  action_type = action.getActionType()
  """
  if not action.isVisible():
    continue
  if ('Template' in action.getParentTitle()):
    continue
  if (action_type in ['object_button']):
    continue
  # if (action_type in ['object_report', 'object_exchange']):
  #   continue
  if ('web' in action_type) or ('jio' in action_type) or (action_type in ['object_view', 'object_list', 'object_sort', 'object_ui', 'object_search']):
    continue
  """

  if 'Base_viewDocumentList' not in (action.getActionText() or ''):
    continue
  if 'only' in action.getActionType():
    continue
  """
  action.setActionType('object_onlyxhtml_view')
  action.getParentValue().newContent(
    portal_type='Action Information',
    reference='jump_to_document',
    title='Documents',
    action="string:${object_url}/Base_jumpToRelatedDocumentList",
    action_type='object_onlyjio_jump',
    visible=True,
    priority=1,
    condition="python:portal.Base_checkPermission('document_module', 'View')"
  )
  """
  i += 1
  result += '%s %s %s %s' % (action.getParentTitle(), '<a href="https://softinst114089.host.vifib.net/erp5/web_site_module/renderjs_runner/#/%s?editable=true">%s</a>' % (action.getRelativeUrl(), action.getTitle()), action.getActionType(), '<br>')

result = '--- %i<br>%s' % (i, result)
print result
return printed

#####################################

from DateTime import DateTime
return DateTime()


alarm = context.getPortalObject().portal_alarms.promise_check_upgrade
# return alarm.getLastActiveProcess().getResultList()
return context.getPortalObject().portal_activities['2096'].getResultList()[0].detail

from DateTime import DateTime
return DateTime()

return "OK %s" % str(context.WebSection_getSiteMapTree(depth=99, include_subsection=1, include_document=1))


context.edit(preferred_event_resource=None)
return "ok"

context.getPortalObject().web_site_module.renderjs_runner.edit()
return 'OK'

return context.portal_catalog(reference= {'query': 'aa', 'key':'ExactMatch'}, src__=1)

# return context.getPortalObject().portal_catalog(reference='', src__=1)
# return 'ok'
context.log('--- traverse')
section = context.getPortalObject().restrictedTraverse('web_site_module/3/1')
context.log('--- document')
result = section.getDefaultDocumentValue()
context.log('--- result: %s', result)
return 'couscous'

raise NotImplementedError(context.getPortalObject().restrictedTraverse('web_site_module/3/2//'))


REQUEST = context.REQUEST
raise NotImplementedError(REQUEST.environ.get('HTTP_USER_AGENT'))

from urlparse import urlparse
parse_dict = urlparse(REQUEST.other.get('ACTUAL_URL'))
print parse_dict

print "%s %s %s %s" % (parse_dict.scheme, parse_dict.port, parse_dict.hostname, parse_dict.path)

import urllib
print REQUEST.other.get('SERVER_URL')

print '---'

# request.other

for key, value in REQUEST.items():
  if key.startswith('HTTP') or key.startswith('BASE') or key.startswith('REMOTE') or key.startswith('SERVER') or ('PORT' in key) or ('PATH' in key) or ('URL' in key):
    print "%s: %s" % (key, value)

return printed
return "host%s \n%s %s" % (REQUEST.environ.get('HTTP_HOST'), '', '')




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
  if ('web' in action_type) or ('jio' in action_type) or (action_type in ['object_view', 'object_list', 'object_sort', 'object_ui', 'object_search']):
    continue

  i += 1
  result += '%s %s %s %s' % (action.getParentTitle(), '<a href="%s">%s</a>' % (action.getRelativeUrl(), action.getTitle()), action.getActionType(), '<br>')

result = '--- %i<br>%s' % (i, result)
print result
return printed


return context.getPortalObject().portal_catalog(source_project_title='1234', src__=1)

return context.getPortalObject().portal_catalog(source_project_uid='1234', src__=1)



parameter_list = field.getTemplateField().get_value('default_params')

# Some document subobjects have a workflow, and so, can be only be deleted from some state
# If the listbox does not display them, do not add the state filter parameter
filter_portal_type_list = [x[1] for x in parameter_list if x[0] == 'portal_type']
if filter_portal_type_list:
  if sametype(filter_portal_type_list, ''):
    filter_portal_type_list = [filter_portal_type_list]
else:
  filter_portal_type_list = None

return parameter_list + context.Module_listWorkflowTransitionItemList(filter_portal_type_list=filter_portal_type_list)









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
