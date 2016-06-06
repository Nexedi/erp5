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
            <value> <string># Return a list of translated strings corresponding to errors for this movement validity\n
Base_translateString = context.Base_translateString\n
\n
def translateString(msg):\n
  try:\n
    msg = msg.get(\'msg\')\n
    mapping = msg.get(\'mapping\')\n
  except AttributeError:\n
    mapping = None\n
  if translate is None:\n
    return msg\n
  translate_kw = {\'catalog\':\'content\'}\n
  if mapping is not None:\n
    translate_kw[\'mapping\'] = mapping\n
  return Base_translateString(msg, **translate_kw)\n
\n
\n
error_list = context.checkImmobilisationConsistency(to_translate=1)\n
if len(error_list) == 0:\n
  return [Base_translateString(\'Valid\')]\n
\n
translated_list = []\n
for error in error_list:\n
  object = context.getPortalObject().restrictedTraverse(error[0])\n
  string = translateString(error[3])\n
  object_title = object.getTitle() or object.getId()\n
  translated_list.append(\'%s : %s\' % (object_title, string))\n
return translated_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Immobilisation_getValidityErrorTranslatedList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
