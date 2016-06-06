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

"""\n
  The main search script. Receives one big string - a searchabletext, in\n
  the search syntax, parses the string using external method Base_parseSearchString,\n
  then does the following:\n
    - processes arguments for searching by any category\n
    - selects search mode\n
    - adds creation and modification date clauses\n
    - searches\n
    - if requested, filters result so that only the user\'s docs are returned\n
    - if requested, filters result to return only the newest versions\n
"""\n
portal = context.getPortalObject()\n
\n
query_kw = {}\n
date_format = \'%Y-%m-%d\'\n
\n
if searchabletext is None:\n
  # searchabletext can be supplied in request (fallback)\n
  searchabletext = context.REQUEST.get(\'searchabletext\')\n
  \n
if searchabletext is None:\n
  # or in selection\n
  selection_id = \'search_advanced_dialog_selection\'\n
  selection_object = portal.portal_selections.getSelectionParamsFor(selection_id)\n
  if selection_object:\n
    searchabletext = selection_object.get(\'searchabletext\')\n
\n
if searchabletext is None:\n
  raise ValueError, "No search string specified."\n
\n
parsed_search_string = context.Base_parseSearchString(searchabletext)\n
\n
# if no portal type specified, take all\n
portal_type = parsed_search_string.get(\'portal_type\', None)\n
if portal_type is None or not len(portal_type):\n
  query_kw[\'portal_type\'] = portal.getPortalDocumentTypeList()\n
else:\n
  # safe to add passed portal_type, \n
  # as multiple values exists split them by \',\'\n
  query_kw[\'portal_type\'] = portal_type.split(\',\')\n
\n
# ZSQLCatalog wants table.key to avoid ambiguity\n
parsed_searchabletext = parsed_search_string.get(\'searchabletext\', None)\n
if parsed_searchabletext is not None: \n
  query_kw[\'full_text.SearchableText\'] =  parsed_searchabletext\n
\n
for key in (\'reference\', \'version\', \'language\',):\n
  value = parsed_search_string.get(key, None)\n
  if value is not None:\n
    query_kw[key] = value\n
\n
where_expression_list = []\n
creation_from = parsed_search_string.get(\'creation_from\', None)\n
creation_to = parsed_search_string.get(\'creation_to\', None)\n
modification_from = parsed_search_string.get(\'modification_from\', None)\n
modification_to = parsed_search_string.get(\'modification_to\', None)\n
if creation_from:\n
  where_expression_list.append(\'catalog.creation_date >= "%s"\' \\\n
                                 %creation_from.strftime(date_format))\n
if creation_to:\n
  where_expression_list.append(\'catalog.creation_date <= "%s"\' \\\n
                                 %creation_to.strftime(date_format))\n
if modification_from:\n
  where_expression_list.append(\'catalog.modification_date >= "%s"\' \\\n
                                 %modification_from.strftime(date_format))\n
if modification_to:\n
  where_expression_list.append(\'catalog.modification_date <= "%s"\' \\\n
                                 %modification_to.strftime(date_format))\n
if len(where_expression_list):\n
  query_kw[\'where_expression\'] = \' AND \'.join(where_expression_list)\n
\n
if parsed_search_string.get(\'mine\', None) is not None:\n
  # user wants only his documents\n
  query_kw[\'owner\'] = str(portal.portal_membership.getAuthenticatedMember())\n
\n
# add contributor title\n
contributor_title = parsed_search_string.get(\'contributor_title\', None)\n
if contributor_title is not None:\n
  query_kw[\'contributor_title\'] = contributor_title\n
\n
if parsed_search_string.get(\'newest\', None) is not None:\n
  #...and now we check for only the newest versions\n
  # but we need to preserve order\n
  query_kw[\'group_by\'] = (\'reference\',)\n
  result = [doc.getLatestVersionValue() \\\n
              for doc in context.portal_catalog(**query_kw)]\n
else:\n
  result = portal.portal_catalog(**query_kw)\n
\n
return result\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>searchabletext=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getAdvancedSearchResultList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
