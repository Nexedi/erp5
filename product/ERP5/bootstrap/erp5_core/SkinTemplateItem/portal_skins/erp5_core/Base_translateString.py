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
  Translate message into another language.\n
  If \'lang\' is omitted a selected user interface language is used.\n
  Can use any of existing message catalogs (default is \'ui\').\n
"""\n
\n
from Products.CMFCore.utils import getToolByName\n
translation_service = getToolByName(context, \'Localizer\', None)\n
if translation_service is not None :\n
  try:\n
    if not encoding:\n
      return translation_service.translate(catalog, msg, lang=lang, **kw)\n
    msg = translation_service.translate(catalog, msg, lang=lang, **kw)\n
    if same_type(msg, u\'\'):\n
      msg = msg.encode(encoding)\n
    return msg\n
  except AttributeError: # This happens in unit testing, because it is not able to find something with get_context()\n
    pass\n
\n
return msg\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>msg, catalog="ui", encoding=\'utf8\', lang=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_translateString</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
