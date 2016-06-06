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
            <value> <string>from Products.ZSQLCatalog.SQLCatalog import ComplexQuery\n
from Products.ZSQLCatalog.SQLCatalog import Query\n
\n
# Get the list of parent messages\n
attachment_pdf_list=[]\n
current_object = context.getObject()\n
event_list = current_object.getFollowUpRelatedValueList()\n
attachment_list =[x.getAggregateValueList() for x in event_list]\n
for y in attachment_list:\n
 attachment_pdf_list.extend(filter(lambda x:(x.getPortalType()==\'PDF\'),y))\n
event_uid_list = map(lambda x: x.getUid(), event_list)\n
attachment_pdf_uid_list =[x.getUid() for x in attachment_pdf_list]\n
\n
if not event_uid_list:\n
 return []\n
\n
# Build query\n
query = ComplexQuery(Query(parent_uid=event_uid_list),\n
                     Query(uid=event_uid_list),\n
                     Query(parent_uid=attachment_pdf_uid_list),\n
                     Query(uid=attachment_pdf_uid_list),\n
                     operator="OR")\n
\n
kw[\'portal_type\'] = (\'PDF\',\'Image\') + context.getPortalDocumentTypeList()+context.getPortalEventTypeList()\n
return context.portal_catalog(query=query, **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>testImageRequest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
