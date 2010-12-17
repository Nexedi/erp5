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
            <value> <string>"""Check the object have an unique reference in it\'s parent folder\n
"""\n
from Products.ERP5Type.Log import log\n
if editor is None : \n
  return 1\n
\n
reference = editor\n
\n
document = context.restrictedTraverse(request.object_path, None)\n
if document is None : \n
  log(\'Base_uniqueReferenceInFolderValidator\', \'document is None\')\n
  return 0\n
\n
parent_folder = document.getParentValue()\n
for same_reference in parent_folder.searchFolder(reference = reference):\n
  if same_reference.uid != document.getUid() :\n
    log(\'Base_uniqueReferenceInFolderValidator\',\n
                        \'another document with reference %s exists at %s\' % (reference, same_reference.getPath()))\n
    return 0\n
\n
return 1\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>editor, request</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_uniqueReferenceInFolderValidator</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
