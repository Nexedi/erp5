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
Return a list of diff objects between two business templates.\n
The building state of the business templates should be "built".\n
\n
Arguments:\n
\n
- ``bt1``: The first business template object to compare\n
- ``bt2``: The second business template object to compare\n
"""\n
from Products.ERP5Type.Document import newTempBase\n
from ZODB.POSException import ConflictError\n
\n
template_tool = context.getPortalObject().portal_templates\n
\n
assert bt1.getBuildingState() == "built"\n
assert bt2.getBuildingState() == "built"\n
\n
modified_object_list = bt2.preinstall(check_dependencies=0, compare_to=bt1)\n
keys = modified_object_list.keys()\n
#keys.sort() # XXX don\'t care ?\n
bt1_id = bt1.getId()\n
bt2_id = bt2.getId()\n
i = 0\n
object_list = []\n
for object_id in keys:\n
  object_state, object_class = modified_object_list[object_id]\n
  line = newTempBase(template_tool, \'tmp_install_%s\' % str(i)) # template_tool or context?\n
  line.edit(object_id=object_id, object_state=object_state, object_class=object_class, bt1=bt1_id, bt2=bt2_id)\n
  line.setUid(\'new_%s\' % object_id)\n
  if detailed and object_state == "Modified":\n
    try:\n
      line.edit(data=bt2.diffObject(line, compare_with=bt1_id))\n
    except ConflictError:\n
      raise\n
    except Exception as e:\n
      if raise_on_diff_error:\n
        raise\n
      line.edit(error=repr(e))\n
  object_list.append(line)\n
  i += 1\n
return object_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>bt1, bt2, detailed=False, raise_on_diff_error=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getBusinessTemplateDiffObjectList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
