from ZTUtils import make_query
from Products.PythonScripts.standard import url_quote

REQUEST = container.REQUEST
RESPONSE = REQUEST.RESPONSE
selection_name = kw['list_selection_name']

uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)

if len(uids) == 0:
  return context.REQUEST.RESPONSE.redirect(
           '%s/TemplateTool_viewInstallRepositoryBusinessTemplateListDialog?'
           'portal_status_message=%s' % ( context.absolute_url(),
                               url_quote('No Business Template Selected.')))

# Initilization
title_list = []
portal_status_message = ''
current_uid_list = []
installed_business_template_title_list = context.getInstalledBusinessTemplateTitleList()

for uid in uids:
  current_uid_list.append(uid)
  repository, bt5_id = context.decodeRepositoryBusinessTemplateUid(uid)
  title_list.append(bt5_id.replace(".bt5", ""))

available_bt5_list = context.getRepositoryBusinessTemplateList()

# Check for missing dependencies
for uid in uids:
  repository, bt5_id = context.decodeRepositoryBusinessTemplateUid(uid)
  bt5_title = bt5_id.replace(".bt5", "")
  dependency_list = context.getDependencyList((repository, bt5_id))
  for dep_repository, dep_id in dependency_list:
    dep_title = dep_id.replace(".bt5", "")
    if dep_title != bt5_title and \
        dep_title in installed_business_template_title_list:
      continue
    if dep_title not in title_list:
      title_list.append(dep_title)
      if dep_repository != 'meta':
        portal_status_message+='\'%s\' added because \'%s\' depends on it.'%(dep_title, bt5_title)
        current_uid_list.append(context.encodeRepositoryBusinessTemplateUid(dep_repository, dep_id))
      else:
        provider_list = context.getProviderList(dep_id)
        if len([x for x in provider_list if x in title_list]) == 0:
          # No provider installed
          if len(provider_list) == 1:
            # When only one provider is possible, use it
            provider = provider_list[0]
            for candidate in available_bt5_list:
              if candidate.title == provider:
                current_uid_list.append(candidate.uid)
                break
            portal_status_message+='\'%s\' added because \'%s\' depends on it.'%(provider, bt5_title)
          else:
            portal_status_message+='\'%s\' requires you to select one of the following business templates: %s'%(bt5_title, provider_list)

# If somes dependencies were missing
# we call the dialog again with the
# new bts selected
if portal_status_message != '' :
  context.portal_selections.setSelectionCheckedUidsFor('template_tool_install_selection', current_uid_list)
  return context.REQUEST.RESPONSE.redirect(
    '%s/TemplateTool_viewInstallRepositoryBusinessTemplateListDialog?portal_status_message=%s'
    % (context.absolute_url(), url_quote(portal_status_message)))

# order uids according to dependencies before processing
tuple_list = []
for uid in uids:
  tuple_list.append(context.decodeRepositoryBusinessTemplateUid(uid))
tuple_list = context.sortBusinessTemplateList(tuple_list)


bt_list = []
for repository, id_ in tuple_list:
  bt = context.download('/'.join([repository, id_]))
  bt_list.append(bt.getId())

RESPONSE.redirect(
  '%s/TemplateTool_viewMultiInstallationDialog?%s&form_id=BusinessTemplate_installationChoice'
  % (context.absolute_url(), make_query({'bt_list' : bt_list})))
