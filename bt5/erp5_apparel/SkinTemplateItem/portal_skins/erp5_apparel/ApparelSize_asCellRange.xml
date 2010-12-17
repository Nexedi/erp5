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
            <value> <string>if matrixbox == 1:\n
  column = [  (\'apparel_morpho_type/\'+x.getId(),x.getTranslatedTitle()) for x in context.getApparelMorphoTypeValueList()]\n
  line = [ (\'size/\'+x.getId(),x.getTranslatedTitle()) for x in context.getSizeValueList()]\n
else:\n
  column = [  \'apparel_morpho_type/\'+x.getId() for x in context.getApparelMorphoTypeValueList()]\n
  line = [ \'size/\'+x.getId() for x in context.getSizeValueList()]\n
\n
tab = []\n
\n
cell_range = [line, column, tab]\n
\n
return cell_range\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>matrixbox=0, base_id=None, display_base_category=1, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ApparelSize_asCellRange</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
