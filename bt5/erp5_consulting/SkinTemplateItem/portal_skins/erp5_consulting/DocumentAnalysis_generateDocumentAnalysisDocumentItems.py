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
            <value> <string>context_obj = context.getObject()\n
\n
role_type = \'Document Analysis Document Item\'\n
\n
# this list contain all items\n
items = []\n
\n
# get the user information\n
for line in listbox:\n
  if line.has_key(\'listbox_key\') and line[\'item_title\'] not in (\'\', None):\n
    line_id = int(line[\'listbox_key\'])\n
    item = {}\n
    item[\'id\'] = line_id\n
    item[\'title\'] = line[\'item_title\']\n
    item[\'description\'] = line[\'item_description\']\n
    items.append(item)\n
\n
# sort the list by id to have the same order of the user\n
items.sort(lambda x, y: cmp(x[\'id\'], y[\'id\']))\n
\n
# create corresponding objects\n
for item in items:\n
  context_obj.newContent( portal_type        = role_type\n
                        , title              = item[\'title\']\n
                        , description        = item[\'description\']\n
                        )\n
\n
# return to the feature module\n
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + \'?portal_status_message=\' + role_type.replace(\' \', \'+\') + \'(s)+added.\')\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox=[], **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DocumentAnalysis_generateDocumentAnalysisDocumentItems</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
