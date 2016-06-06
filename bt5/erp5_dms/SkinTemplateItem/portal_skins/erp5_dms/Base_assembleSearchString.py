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
            <value> <string>"""\n
  This script receives a request from advanced search form and \n
  puts together a search string in a search syntax, depending on\n
  parameters received. \n
  It is the reverse of Base_parseSearchString script.\n
"""\n
MARKER = [\'\', None]\n
BOOLEAN_MARKER = MARKER + [0]\n
request = context.REQUEST\n
\n
# one can specify a direct search string, \n
# in this case simply returning it is expected\n
searchabletext = kw.get(\'searchabletext\', \n
                        request.get(\'searchabletext\', None))\n
if searchabletext not in MARKER:\n
  return searchabletext\n
\n
# words to search in \'any of the words\' form - left intact\n
searchabletext_any = kw.get(\'searchabletext_any\', \n
                            request.get(\'searchabletext_any\', \'\'))\n
search_string = searchabletext_any\n
\n
# exact phrase to search for double-quoted\n
searchabletext_phrase = kw.get(\'searchabletext_phrase\', \n
                               request.get(\'searchabletext_phrase\', None))\n
if searchabletext_phrase not in MARKER:\n
  search_string += \' \\"%s\\"\' %searchabletext_phrase\n
\n
# search "with all of the words" - each word prefixed by "+"\n
searchabletext_all = kw.get(\'searchabletext_all\',\n
                            request.get(\'searchabletext_all\', None))\n
if searchabletext_all not in MARKER:\n
  search_string += \'  %s\' %\' \'.join(\'+%s\' %word for word in searchabletext_all.split(\' \'))\n
\n
# search without these words - every word prefixed by "-"\n
searchabletext_without = kw.get(\'searchabletext_without\',\n
                                request.get(\'searchabletext_without\', None))\n
if searchabletext_without not in MARKER:\n
  search_string += \' %s\'  %\' \'.join(\'-%s\' %word for word in searchabletext_without.split(\' \'))\n
\n
# search limited to a certain date range - add "created:xxx"\n
created_within = kw.get(\'created_within\', request.get(\'created_within\', None))\n
if created_within not in MARKER:\n
  search_string += \' created:%s\' %created_within\n
\n
# only given portal_types - add "type:Type" or type:(Type1,Type2...)\n
portal_type_list = kw.get(\'search_portal_type\', \n
                          request.get(\'search_portal_type\'))\n
if portal_type_list == \'all\':\n
  portal_type_list=None\n
if isinstance(portal_type_list, str):\n
  portal_type_list=[portal_type_list]\n
if portal_type_list:\n
  portal_type_string_list = []\n
  for portal_type in portal_type_list:\n
    if \' \' in portal_type:\n
      portal_type = \'"%s"\' %portal_type\n
    portal_type_string_list.append(\'portal_type:%s\' %portal_type)\n
  portal_type_string = \'(%s)\' %\' OR \'.join(portal_type_string_list)\n
  if search_string not in MARKER:\n
    search_string += \' %s %s\' %(logical_operator, portal_type_string)\n
  else:\n
    search_string += portal_type_string\n
\n
# search by reference\n
reference = kw.get(\'reference\', request.get(\'reference\', None))\n
if reference not in MARKER:\n
  search_string += \' reference:%s\' % reference\n
\n
# search by version\n
version = kw.get(\'version\', request.get(\'version\'))\n
if version not in MARKER:\n
  search_string += \' version:%s\' %version\n
\n
# search by language\n
language=kw.get(\'language\', request.get(\'language\', None))\n
if language not in MARKER and language != \'0\':\n
  search_string += \' language:%s\' % language\n
\n
# category search\n
for category in (\'group\', \'site\', \'function\', \'publication_section\', \'classification\'):\n
  category_field_id = \'subfield_field_your_category_list_%s\' %category\n
  category_value = kw.get(category_field_id, request.get(category_field_id, None))\n
  if category_value not in MARKER:\n
    search_string += \' %s:%s\' % (category, category_value)\n
\n
# contributor title search\n
for category in (\'contributor_title\',):\n
  category_value = kw.get(category, request.get(category, None))\n
  if category_value not in MARKER:\n
    search_string += \' %s:%s\' %(category, category_value)\n
\n
# only my docs\n
mine = kw.get(\'mine\', request.get(\'mine\', None))\n
if mine not in BOOLEAN_MARKER:\n
  search_string += \' mine:yes\'\n
\n
# only newest versions\n
newest =  kw.get(\'newest\', request.get(\'newest\', None))\n
if newest not in BOOLEAN_MARKER:\n
  search_string += \' newest:yes\'\n
\n
# search mode\n
search_mode = kw.get(\'search_mode\', request.get(\'search_mode\', None))\n
search_mode_map={\'in_boolean_mode\':\'boolean\',\n
                 \'with_query_expansion\':\'expanded\'}\n
if search_mode not in MARKER and search_mode_map.has_key(search_mode):\n
  search_string += \' mode:%s\' % search_mode_map[search_mode]\n
\n
return search_string\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>logical_operator=\'AND\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_assembleSearchString</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
