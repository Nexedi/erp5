<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

from ZTUtils import make_query\n
from Products.PythonScripts.standard import url_quote\n
\n
REQUEST = container.REQUEST\n
RESPONSE = REQUEST.RESPONSE\n
selection_name = kw[\'list_selection_name\']\n
\n
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)\n
\n
if len(uids) == 0:\n
  return context.REQUEST.RESPONSE.redirect(\n
           \'%s/TemplateTool_viewInstallRepositoryBusinessTemplateListDialog?\'\n
           \'portal_status_message=%s\' % ( context.absolute_url(),\n
                               url_quote(\'No Business Template Selected.\')))\n
\n
# Initilization\n
title_list = []\n
portal_status_message = \'\'\n
current_uid_list = []\n
installed_business_template_title_list = context.getInstalledBusinessTemplateTitleList()\n
\n
for uid in uids:\n
  current_uid_list.append(uid)\n
  repository, bt5_id = context.decodeRepositoryBusinessTemplateUid(uid)\n
  title_list.append(bt5_id.replace(".bt5", ""))\n
\n
available_bt5_list = context.getRepositoryBusinessTemplateList()\n
\n
# Check for missing dependencies\n
for uid in uids:\n
  repository, bt5_id = context.decodeRepositoryBusinessTemplateUid(uid)\n
  bt5_title = bt5_id.replace(".bt5", "")\n
  dependency_list = context.getDependencyList((repository, bt5_id))\n
  for dep_repository, dep_id in dependency_list:\n
    dep_title = dep_id.replace(".bt5", "")\n
    if dep_title != bt5_title and \\\n
        dep_title in installed_business_template_title_list:\n
      continue\n
    if dep_title not in title_list:\n
      title_list.append(dep_title)\n
      if dep_repository != \'meta\':\n
        portal_status_message+=\'\\\'%s\\\' added because \\\'%s\\\' depends on it.\'%(dep_title, bt5_title)\n
        current_uid_list.append(context.encodeRepositoryBusinessTemplateUid(dep_repository, dep_id))\n
      else:\n
        provider_list = context.getProviderList(dep_id)\n
        if len([x for x in provider_list if x in title_list]) == 0:\n
          # No provider installed\n
          if len(provider_list) == 1:\n
              # When only one provider is possible, use it\n
              provider = provider_list[0]\n
              for candidate in available_bt5_list:\n
                if candidate.title == provider:\n
                  current_uid_list.append(candidate.uid)\n
                  break\n
              portal_status_message+=\'\\\'%s\\\' added because \\\'%s\\\' depends on it.\'%(provider, bt5_title)\n
          else:\n
            portal_status_message+=\'\\\'%s\\\' requires you to select one of the following business templates: %s\'%(bt5_title, provider_list)\n
\n
# If somes dependencies were missing\n
# we call the dialog again with the\n
# new bts selected\n
if portal_status_message != \'\' :\n
  context.portal_selections.setSelectionCheckedUidsFor(\'template_tool_install_selection\', current_uid_list)\n
  return context.REQUEST.RESPONSE.redirect(\n
    \'%s/TemplateTool_viewInstallRepositoryBusinessTemplateListDialog?portal_status_message=%s\'\n
    % (context.absolute_url(), url_quote(portal_status_message)))\n
\n
# order uids according to dependencies before processing\n
tuple_list = []\n
for uid in uids:\n
  tuple_list.append(context.decodeRepositoryBusinessTemplateUid(uid))\n
tuple_list = context.sortBusinessTemplateList(tuple_list)\n
\n
\n
bt_list = []\n
for repository, id in tuple_list:\n
  bt = context.download(\'/\'.join([repository, id]))\n
  bt_list.append(bt.getId())\n
\n
RESPONSE.redirect(\n
  \'%s/TemplateTool_viewMultiInstallationDialog?%s&form_id=BusinessTemplate_installationChoice\'\n
  % (context.absolute_url(), make_query({\'bt_list\' : bt_list})))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TemplateTool_installRepositoryBusinessTemplateList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
