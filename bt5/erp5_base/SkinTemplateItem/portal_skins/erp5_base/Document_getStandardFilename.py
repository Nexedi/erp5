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
  This script returns a standard file name, build from reference, version and\n
  language (this is only the base part of the name, the extension should be appended\n
  in another place). It does the reverse of getPropertyDictFromFilename, so changes in\n
  filename parsing regular expression should be reflected here.\n
  It is used as a type-based method.\n
"""\n
original_filename = context.getFilename(\'\')\n
original_extension = None\n
if \'.\' in original_filename:\n
  original_filename, original_extension = original_filename.rsplit(\'.\', 1)\n
if context.hasReference():\n
  filename = context.getReference()\n
elif original_filename:\n
  filename = original_filename\n
else:\n
  filename = context.getTitleOrId()\n
if context.hasVersion():\n
  filename = \'%s-%s\' % (filename, context.getVersion(),)\n
if context.hasLanguage():\n
  filename = \'%s-%s\' % (filename, context.getLanguage(),)\n
if format or original_extension:\n
  extension = (format or original_extension).split(\'.\')[-1]\n
  filename = \'%s.%s\' % (filename, extension,)\n
return filename\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>format=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_getStandardFilename</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
