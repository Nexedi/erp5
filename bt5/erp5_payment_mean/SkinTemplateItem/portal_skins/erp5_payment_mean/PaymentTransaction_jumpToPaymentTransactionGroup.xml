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
            <value> <string>translateString = context.Base_translateString\n
portal_type = \'Payment Transaction Group\'\n
\n
for line in context.getMovementList(\n
        portal_type=context.getPortalAccountingMovementTypeList()):\n
\n
  related_object = line.getAggregateValue(portal_type=portal_type)\n
\n
  if related_object is not None:\n
    url = related_object.absolute_url()\n
    return related_object.Base_redirect(\'view\', keep_items=dict(\n
      portal_status_message=translateString(\n
      # first, try to get a full translated message with portal types\n
      "%s related to %s." % (related_object.getPortalType(), context.getPortalType()),\n
       # if not found, fallback to generic translation\n
      default = unicode(translateString(\'${this_portal_type} related to ${that_portal_type} : ${that_title}.\',\n
        mapping={"this_portal_type" : related_object.getTranslatedPortalType(),\n
                 "that_portal_type" : context.getTranslatedPortalType(),\n
                 "that_title" : context.getTitleOrId() }), \'utf8\'))))\n
\n
return context.Base_redirect(\'view\', keep_items=dict(\n
    portal_status_message=translateString(\n
    \'No %s Related\' % portal_type,\n
    default = unicode(translateString(\'No ${portal_type} related.\',\n
                                           mapping = { \'portal_type\': translateString(portal_type)}), \'utf8\'))))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaymentTransaction_jumpToPaymentTransactionGroup</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
