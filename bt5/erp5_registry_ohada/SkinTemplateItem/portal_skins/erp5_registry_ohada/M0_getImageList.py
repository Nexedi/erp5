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

from Products.ZSQLCatalog.SQLCatalog import ComplexQuery\n
from Products.ZSQLCatalog.SQLCatalog import Query\n
"""\n
  This script creates a list Person objects based\n
  on the M0 form information. It updates the list of persons\n
  based on fast input entries.\n
"""\n
from string import zfill\n
global result_list\n
global uid\n
uid = 0\n
result_list = []\n
request = context.REQUEST\n
listbox = getattr(request, \'listbox\', None) # Retrieve the fast input data if any\n
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
kw[\'portal_type\'] = (\'PDF\')\n
result_uid = [x.getUid() for x in context.portal_catalog(query=query, **kw)]\n
result_document = [x.getObject() for x in context.portal_catalog(query=query, **kw)]\n
display = \'thumbnail\'\n
format = \'jpg\'\n
resolution =\'75\'\n
for doc in result_document:\n
   content_information = doc.getContentInformation()\n
   page_number = int(content_information.get(\'Pages\', 0))\n
   page_list = range(page_number)\n
   page_number_list = []\n
   for i in page_list:\n
     url = \'%s?display=%s&format=%s&resolution=%s&frame=%s\'%(doc.absolute_url(),\n
                                  display,format,resolution,i)\n
     new_doc = doc.asContext(thumbnail=url)\n
     result_list.append(new_doc)\n
     page_number_list.append(i)\n
\n
listbox = getattr(result_list, \'listbox\', None)\n
return result_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>lines_num=8, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>M0_getImageList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
