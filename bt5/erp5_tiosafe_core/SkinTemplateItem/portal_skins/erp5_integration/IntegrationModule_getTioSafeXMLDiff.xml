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
            <value> <string>im = context\n
pub_source = im.getSourceSectionValue().getSourceValue()\n
pub_list = im.getSourceSectionValue().getListMethodId()\n
pub_xml_method = im.getSourceSectionValue().getXmlBindingGeneratorMethodId()\n
sub_source = im.getDestinationSectionValue().getSourceValue()\n
sub_list = im.getDestinationSectionValue().getListMethodId()\n
sub_xml_method = im.getDestinationSectionValue().getXmlBindingGeneratorMethodId()\n
\n
pub_method = getattr(pub_source, pub_list, None)\n
sub_method = getattr(sub_source, sub_list, None)\n
\n
pub_xml = []\n
sub_xml = []\n
def tiosafe_sort(a,b):\n
  if getattr(a, \'email\', None):\n
    return cmp(a.email, b.email)\n
  elif getattr(a, \'getDefaultEmailText\', None) and len(a.getDefaultEmailText("")):\n
    return cmp(a.getDefaultEmailText(), b.getDefaultEmailText())\n
  elif getattr(a, \'reference\', None):\n
    return cmp(a.reference, b.reference)\n
  elif getattr(a, \'getReference\', None) and len(a.getReference("")):\n
    return cmp(a.getReference(), b.getReference())\n
  elif getattr(a, \'title\', None):\n
    return cmp(a.title, b.title)\n
  else:\n
    return cmp(a.id, b.id)\n
  \n
\n
if pub_method is not None and sub_method is not None:\n
  pub_object = pub_method(context_document=im.getSourceSectionValue())\n
  pub_object.sort(cmp=tiosafe_sort)\n
  for ob in pub_object:\n
    try:\n
      pub_xml.append(getattr(ob, pub_xml_method)(context_document=im.getSourceSection()))\n
    except TypeError:\n
      pub_xml.append(getattr(ob, pub_xml_method)())\n
\n
  sub_object = sub_method(context_document=im.getDestinationSectionValue())\n
  sub_object.sort(cmp=tiosafe_sort)\n
  for ob in sub_object:\n
    try:\n
      sub_xml.append(getattr(ob, sub_xml_method)(context_document=im.getDestinationSection()))\n
    except TypeError:\n
      sub_xml.append(getattr(ob, sub_xml_method)())\n
\n
else:\n
  raise ValueError, "Impossible to get method, pub_method = %s from %s, sub_method = %s from %s" %(pub_method, pub_list, sub_method, sub_list,)\n
\n
pub_xml = \'\\n\'.join(pub_xml)\n
sub_xml = \'\\n\'.join(sub_xml)\n
\n
return context.diffXML(xml_plugin=sub_xml, xml_erp5=pub_xml, html=html)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>html=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationModule_getTioSafeXMLDiff</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
