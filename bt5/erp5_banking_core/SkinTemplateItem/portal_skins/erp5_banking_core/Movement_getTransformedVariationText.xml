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

parent_portal_type = context.getParent().getPortalType()\n
variation_dict = {}\n
for variation in context.getVariationText().split(\'\\n\') :\n
  variation_list = variation.split(\'/\', 1)\n
  if len(variation_list) == 2 :\n
    variation_dict[variation_list[0]] = variation_list[1]\n
# fonctionne uniquement pour les cellule : dans le cas des lignes: les autres valaures sont ecrasé\n
dest_variation_dict = variation_dict.copy()\n
##########################################\n
\n
\n
# ceci est une transformation\n
# -> quand on fait une destruction de billet, une Destruction Line avec cash status to delete\n
# -> en source cash_status = to_delete; en destination cash_status = cancelled\n
# Faire la liste des modules qui demandent une transformation et coder la liste des modules en dur ici\n
#  avec les variations à forcer.\n
\n
if 0 and parent_portal_type == \'Cash To Currency Purchase Line Out\' :\n
  variation_dict[\'emission_letter\'] = \'k\'\n
  dest_variation_dict[\'cash_status\'] = \'cancelled\'\n
\n
##########################################\n
variation_list = [\'%s/%s\' % (k, v) for k, v in variation_dict.items()]\n
dest_variation_list = [\'%s/%s\' % (k, v) for k, v in dest_variation_dict.items()]\n
variation_list.sort() ; dest_variation_list.sort()\n
return [\'\\n\'.join(variation_list), \'\\n\'.join(dest_variation_list)]\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Movement_getTransformedVariationText</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
