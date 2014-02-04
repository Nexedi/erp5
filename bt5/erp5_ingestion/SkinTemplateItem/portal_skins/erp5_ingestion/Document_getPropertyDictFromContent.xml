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
This script analyzes the document content to find properties that might\n
be somehow encoded in the text. It is called by Document.getPropertyDictFromContent\n
method.\n
\n
To use, write your own method (probably External Method, since it is most likely\n
to use re) that would analyze text content of the doc\n
and return a dictionary of properties.\n
"""\n
information = context.getContentInformation()\n
\n
result = {}\n
property_id_list = context.propertyIds()\n
for k, v in information.items():  \n
  key = k.lower()\n
  if v:\n
    if isinstance(v, unicode): v = v.encode(\'utf-8\')\n
    if key in property_id_list:\n
      if key == \'reference\':\n
        pass # XXX - We can not trust reference on getContentInformation\n
      else:\n
        result[key] = v\n
    elif key == \'author\':\n
      p = context.portal_catalog.getResultValue(title = v)\n
      if p is not None:\n
        result[\'contributor\'] = p.getRelativeUrl()\n
    elif key == \'keywords\':\n
      if isinstance(v, (list, tuple)):\n
        v = [isinstance(x, unicode) and x.encode(\'utf-8\') or x for x in v]\n
      else:\n
        v = v.split()\n
      result[\'subject_list\'] = v\n
\n
# Erase titles which are meaningless\n
title = result.get(\'title\', None)\n
if title:\n
  if title.startswith(\'Microsoft Word\'):\n
    # Probably a file generated from MS Word\n
    del result[\'title\']\n
  elif title==context.getId() and not context.title:\n
    # this is not a true title, but just an id.\n
    del result[\'title\']\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_getPropertyDictFromContent</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
