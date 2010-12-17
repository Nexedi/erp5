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
            <value> <string>request = context.REQUEST\n
domain_list = []\n
\n
if depth == 0:\n
  module = context.task_module\n
\n
  domain = parent.generateTempDomain(id=\'sub%s\' % module.getId())\n
  domain.edit(title=module.getTitle(),\n
              membership_criterion_base_category=(\'parent\', ), \n
              membership_criterion_category=(module.getRelativeUrl(),),\n
              domain_generator_method_id=script.id,\n
              uid=module.getUid())\n
  return [domain]\n
else:\n
  return []\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>depth, parent, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaskModule_generateDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
