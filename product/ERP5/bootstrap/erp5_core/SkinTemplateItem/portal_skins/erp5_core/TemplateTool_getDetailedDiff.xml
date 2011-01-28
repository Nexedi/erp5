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

ZMI_OBJECT_CLASS_LIST = ["Skin"]\n
ERP5_OBJECT_CLASS_LIST = ["Path", "Category", "PortalType", "Module"]\n
PORTAL_TYPE_OBJECT_LIST = ["PortalTypePropertySheet", "PortalTypeBaseCategory", \n
                           "PortalTypeBaseCategory", "PortalTypeAllowedContentType"]\n
WORKFLOW_OBJECT_CLASS_LIST = [\'PortalTypeWorkflowChain\']\n
\n
color_dict = { \'Modified\' : \'#FDE406\', \n
               \'New\' : \'#B5FFB5\', \n
               \'Removed\' : \'#FFA4A4\' }\n
link = 0\n
request = context.REQUEST\n
print \'<div style="background-color:white;padding:4px">\'\n
for diff_object in context.BusinessTemplate_getDiffObjectList():\n
  color = color_dict.get(diff_object.object_state, \'#FDE406\')\n
  print \'<div style="background-color:%s;padding:4px">\' % color\n
  # XXX This header could be more improved to have icons and more options, like\n
  # See XML, full diff, unified diff, link to svn (if available).\n
  print \'&nbsp; [<b>%s</b>] [<b>%s</b>] &nbsp;\' % (diff_object.object_state,\n
                                                   diff_object.object_class)\n
\n
  if diff_object.object_class in ERP5_OBJECT_CLASS_LIST:\n
    print \'<a href="%s">\' % (diff_object.object_id)\n
    link = 1\n
  elif diff_object.object_class in PORTAL_TYPE_OBJECT_LIST:\n
    print \'<a href="portal_types/%s">\' % (diff_object.object_id)\n
    link = 1\n
  elif diff_object.object_class in ZMI_OBJECT_CLASS_LIST:\n
    print \'<a href="%s/manage_main">\' % (diff_object.object_id)\n
    link = 1\n
  elif diff_object.object_class in WORKFLOW_OBJECT_CLASS_LIST:\n
    print \'<a href="portal_workflow/manage_main">\'\n
    link = 1\n
  print \'%s\' % (diff_object.object_id)\n
  if link == 1: \n
    print \'</a>\'\n
  print \'</div>\'\n
  if diff_object.object_state.startswith(\'Modified\'):\n
    request.set(\'bt1\', diff_object.bt1)\n
    request.set(\'bt2\', diff_object.bt2)\n
    request.set(\'object_id\', diff_object.object_id)\n
    request.set(\'object_class\', diff_object.object_class)\n
    print context.portal_templates.diffObjectAsHTML(request)\n
  print \'<hr>\'\n
print \'</div>\'\n
return printed\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TemplateTool_getDetailedDiff</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
