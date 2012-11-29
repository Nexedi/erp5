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
Check the workflow history of several foo objects\n
"""\n
from Products.CMFCore.utils import getToolByName\n
\n
foo_module = context.getPortalObject().foo_module\n
wtool = getToolByName(context, \'portal_workflow\')\n
\n
result = \'OK\'\n
error_list = []\n
\n
def assertEquals(a, b, msg=\'\'):\n
  if a != b:\n
    if msg:\n
      error_list.append(msg)\n
    else:\n
      error_list.append(\'%r != %r\' % (a, b))\n
\n
foo_2 = foo_module[\'2\']\n
assertEquals(foo_2.getSimulationState(), \'validated\', \n
             \'Foo 2 state is %s\' % foo_2.getSimulationState())\n
if not error_list:\n
  assertEquals(\n
   wtool.getInfoFor(foo_2, \'history\', wf_id=\'foo_workflow\')[-2][\'comment\'],\n
   \'Comment !\')\n
  assertEquals(\n
   wtool.getInfoFor(foo_2, \'history\', wf_id=\'foo_workflow\')[-2][\'custom_workflow_variable\'],\n
   \'Custom Workflow Variable\')\n
\n
\n
foo_3 = foo_module[\'3\']\n
assertEquals(foo_3.getSimulationState(), \'validated\', \n
             \'Foo 3 state is %s\' % foo_3.getSimulationState())\n
if not error_list:\n
  assertEquals(\n
   wtool.getInfoFor(foo_3, \'history\', wf_id=\'foo_workflow\')[-2][\'comment\'],\n
  \'Comment !\')\n
  assertEquals(\n
   wtool.getInfoFor(foo_2, \'history\', wf_id=\'foo_workflow\')[-2][\'custom_workflow_variable\'],\n
   \'Custom Workflow Variable\')\n
\n
if error_list:\n
  result = \'\'.join(error_list)\n
\n
return \'<html><body><span id="result">%s</span></body></html>\' % result\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_testFolderWorkflowActionCheckCustomDialogWorkflowHistory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
