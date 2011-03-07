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
            <value> <string>from Products.ERP5VCS.SubversionClient import SubversionSSLTrustError, SubversionLoginError\n
from Products.ERP5Type.Document import newTempBase\n
\n
# get selected business templates\n
p = context.getPortalObject()\n
selection_name = \'business_template_selection\' # harcoded because we can also get delete_selection\n
try:\n
  uid, = p.portal_selections.getSelectionCheckedUidsFor(selection_name)\n
except ValueError:\n
  from Products.ERP5.Document.BusinessTemplate import TemplateConditionError\n
  raise TemplateConditionError(\'You can select only one Business Template\')\n
\n
business_template = p.portal_catalog.getObject(uid)\n
return p.REQUEST.RESPONSE.redirect(\n
  business_template.absolute_url_path() + \'/BusinessTemplate_viewVcsLog?added=.\')\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessTemplate_doVcsLogGlobal</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
