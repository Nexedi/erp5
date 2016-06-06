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
 Cache and return a given Web Page as stripped HTML\n
 Use reference and language as cache keys\n
\n
 TODO: remove same script in KM (XXX)\n
"""\n
\n
def getInlinePage(reference, language):\n
 if reference:\n
   page = context.getDocumentValue(reference)\n
   if page is not None:\n
     return page.asStrippedHTML()\n
 return None\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
web_site_url = context.getWebSectionValue().absolute_url()\n
getInlinePage = CachingMethod(getInlinePage, \n
                 id=(\'WebSection_getInlinePageRenderer\', web_site_url))\n
language = context.Localizer.get_selected_language()\n
return getInlinePage(reference, language)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_viewInlinePageRenderer</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
