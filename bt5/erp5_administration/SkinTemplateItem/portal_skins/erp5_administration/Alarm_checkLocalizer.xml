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
  Check that number of untranslated messages for a Localizer MessageCatalog instance\n
  doesn\'t exceed a fixed alarm_warn_ratio.\n
"""\n
alarm_warn_ratio = 0.25\n
\n
localizer = context.Localizer\n
for message_catalog in localizer.objectValues(\'MessageCatalog\'):\n
  all = len(message_catalog.MessageCatalog_getMessageDict().keys())\n
  not_translated = len(message_catalog.MessageCatalog_getNotTranslatedMessageDict().keys())\n
  enable_warning = not_translated > all*alarm_warn_ratio\n
  if enable_warning:\n
    # we have more than allowed number of untranslated messages,\n
    # fire alarm\n
    context.log("Too many untranslated Localizer messages for %s %s/%s" %(message_catalog, all, not_translated))\n
    return True\n
\n
return False\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>activity_count=1, bundle_object_count=100, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_checkLocalizer</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
