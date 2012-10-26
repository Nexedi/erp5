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

"""\n
  This scripts transform used the title of a document\n
  to produce a pretty reference string optimized for Search Engines.\n
\n
  Example:\n
    "New Document - 2006 Edition" -> "new-document-2006-edition"\n
"""\n
translateString = context.Base_translateString\n
\n
title = context.getTitle()\n
if not title:\n
  return context.Base_redirect(form_id,\n
         keep_items = dict(portal_status_message = translateString("Sorry, it is not possible to suggest a reference from an empty title.")), **kw)\n
\n
nice_uri = \'\'\n
\n
for char in title:\n
  if char.isalnum():\n
    nice_uri += char.lower()\n
  elif len(nice_uri) > 0 and nice_uri[-1] != \'-\':\n
    nice_uri += \'-\'\n
\n
context.setReference(nice_uri)\n
return context.Base_redirect(form_id,\n
       keep_items = dict(portal_status_message = translateString("Reference updated.")), **kw)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_suggestReference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
