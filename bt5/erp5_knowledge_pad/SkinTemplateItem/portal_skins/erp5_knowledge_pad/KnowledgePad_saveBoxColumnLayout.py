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
  Save desired user box layout to current knowledge pad.\n
  This script is called by drag and drop framework when user\n
  drags and/or drops a knowledge box to a column.\n
"""\n
if not context.portal_membership.isAnonymousUser():\n
  box_url = None\n
  new_user_layout = []\n
  for item in user_layout.split(\'##\'):\n
    if item != \'\':\n
      l = []\n
      sub_items=item.split(\'|\')\n
      # get box relative url\n
      splitted_box_url = sub_items[0].split(\'_\')\n
      box_url=\'knowledge_pad_module/%s/%s\' %(splitted_box_url[-2], splitted_box_url[-1]) \n
      # remove box_relative_url from layout string\n
      for sub_item in sub_items:\n
        knowledge_box = sub_item.split(\'_\')[-1]\n
        l.append(knowledge_box)\n
      # join boxes\n
      new_user_layout.append(\'|\'.join(l))\n
    else:\n
      new_user_layout.append(item)\n
  # parent is part of layout element\n
  knowledge_pad = context.restrictedTraverse(box_url).getParentValue()\n
  # join columns \n
  new_user_layout = \'##\'.join(new_user_layout)\n
  #  update only if necessary\n
  if getattr(knowledge_pad, \'user_layout\', None)!=new_user_layout:\n
    knowledge_pad.edit(user_layout=new_user_layout)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>user_layout = \'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>KnowledgePad_saveBoxColumnLayout</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Save user preffered layout</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
