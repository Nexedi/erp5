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

from Products.ERP5Type.DiffUtils import DiffFile\n
from Products.PythonScripts.standard import html_quote\n
\n
def sortDiffObjectList(diff_object_list):\n
  return sorted(diff_object_list, key=lambda x: (x.object_state, x.object_class, x.object_id))\n
\n
url_prefix = html_quote(context.getPortalObject().absolute_url())\n
\n
link_configuration = {}\n
for key in ["Skin", "Workflow"]:\n
  link_configuration[key] = \'<a href="\' + url_prefix + \'/%(object_id)s/manage_main">%(object_id)s</a>\' # ZMI\n
link_configuration["PortalTypeWorkflowChain"] = \'<a href="\' + url_prefix + \'/portal_workflow/manage_main">%s</a>\' # ZMI\n
for key in ["Path", "Category", "PortalType", "Module", "PropertySheet"]:\n
  link_configuration[key] = \'<a href="\' + url_prefix + \'/%(object_id)s">%(object_id)s</a>\' # ERP5\n
for key in ["PortalTypePropertySheet", "PortalTypeBaseCategory",\n
            "PortalTypeBaseCategory", "PortalTypeAllowedContentType"]:\n
  link_configuration[key] = \'<a href="\' + url_prefix + \'/portal_types/%(object_id)s">%(object_id)s</a>\' # ERP5\n
link_configuration["Action"] = \'<a href="\' + url_prefix + \'/portal_types/%(object_id)s/../BaseType_viewAction">%(object_id)s</a>\' # ERP5\n
\n
print("<div>")\n
for diff_object in sortDiffObjectList(diff_object_list):\n
  if getattr(diff_object, "error", None) is not None:\n
    print("<p>")\n
    print("Error")\n
    print("(%s) -" % html_quote(diff_object.object_class))\n
    if diff_object.object_class in link_configuration:\n
      print(link_configuration[diff_object.object_class] % {"object_id": html_quote(diff_object.object_id)})\n
    else:\n
      print(html_quote(diff_object.object_id))\n
    print("</p>")\n
    if detailed:\n
      print("<p>")\n
      print(html_quote(diff_object.error))\n
      print("</p>")\n
  else:\n
    print("<p>")\n
    print(html_quote(diff_object.object_state))\n
    print("(%s) -" % html_quote(diff_object.object_class))\n
    if diff_object.object_class in link_configuration:\n
      print(link_configuration[diff_object.object_class] % {"object_id": html_quote(diff_object.object_id)})\n
    else:\n
      print(html_quote(diff_object.object_id))\n
    print("</p>")\n
    if detailed and getattr(diff_object, "data", None) is not None:\n
      print("<div>")\n
      print(DiffFile(diff_object.data).toHTML())\n
      print("</div>")\n
print("</div>")\n
return printed\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>diff_object_list, detailed=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_formatDiffObjectListToHTML</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
