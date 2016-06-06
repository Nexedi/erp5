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
            <value> <string>#from Products.ERP5Type.Log import log\n
request = context.REQUEST\n
object_path = request.get(\'object_path\')\n
if object_path is None:\n
  # Sometimes the object_path not comes with the request, when you edit for example.\n
  object_path = context.REQUEST.get(\'URL1\').split(\'/\')[-1]\n
domain_list = []\n
\n
if depth == 0:\n
  category_list = [ context.task_report_module.getObject() ]  \n
\n
# XXX this is usefull but Breaks the edition\n
#elif depth == 1:\n
#    category_list = context.portal_selections.getSelectionValueList(context=context,\n
#                                                                    selection_name= \'task_report_module_selection\')\n
\n
\n
else:\n
  return domain_list\n
\n
for category in category_list:\n
  domain = parent.generateTempDomain(id = \'sub\' + category.getId() )\n
  domain.edit(title = category.getTitle(),\n
              membership_criterion_base_category = (\'parent\', ), \n
              membership_criterion_category = (category.getRelativeUrl(),),\n
              domain_generator_method_id = script.id,\n
              uid = category.getUid())\n
                \n
  domain_list.append(domain)\n
\n
#log("%s on %s" % (script.getId(), context.getPath()), "%d objects domain" %  len(domain_list))\n
return domain_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>depth, parent, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaskReportModule_generateDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
