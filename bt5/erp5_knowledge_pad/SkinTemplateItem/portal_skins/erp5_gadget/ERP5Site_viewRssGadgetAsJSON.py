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
            <value> <string>from json import dumps\n
\n
request = context.REQUEST\n
\n
# render real gadget content as HTML\n
html = context.ERP5Site_viewRssGadget()\n
box_relative_url = request.get(\'box_relative_url\', None)\n
box = context.restrictedTraverse(box_relative_url)\n
\n
box_dom_id = box.getRelativeUrl().replace(\'/\', \'_\')\n
gadget_title_dom_id = \'%s_gadget_title\' %box_dom_id\n
\n
# return some JavaScript which will update respective page\n
gadget_title = request.get(\'rss_gadget_title\', box.getSpecialiseValue().getTitle())\n
gadget_title = unicode(gadget_title).encode(\'utf-8\')[:40]\n
javascript = \'$("#%s").html("%s");\' %(gadget_title_dom_id, gadget_title)\n
\n
request.RESPONSE.setHeader("Content-Type", "application/json;; charset=utf-8")\n
result =  {"body": html,\n
          "javascript": javascript}\n
return dumps(result)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_viewRssGadgetAsJSON</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
