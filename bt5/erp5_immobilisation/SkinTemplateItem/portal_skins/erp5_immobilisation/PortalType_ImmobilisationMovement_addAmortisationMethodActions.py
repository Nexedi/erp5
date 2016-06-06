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
            <value> <string>from string import capitalize\n
\n
view_id_basis = "%s_%s_amortisation_method_view_details"\n
view_action_basis = "Immobilisation_%s%sAmortisationMethodViewDetails"\n
view_condition_basis = "object/Immobilisation_isUsing%s%sAmortisationMethod"\n
view_permissions_basis = (\'View\',)\n
amortisation_method_view = \'amortisation_method_view\'\n
\n
action_list = context.listActions()\n
\n
print "Making portal type \'%s\' an Immobilisation Movement :" % context.getId()\n
# Add a view for each amortisation method\n
amortisation_method_list = context.Immobilisation_getAmortisationMethodList()\n
for method in amortisation_method_list:\n
  region = method[0]\n
  id = method[1].getId()\n
  title = method[1].title or id\n
  action_id =  view_id_basis % (region, id)\n
\n
  print "- Adding View for method \'%s\'... " % title,\n
\n
  # Check if the action already exists\n
  exists = 0\n
  for action in action_list:\n
    if getattr(action, "id", None) == action_id:\n
      print "already exists"\n
      exists = 1\n
  \n
  if not exists:\n
    capitalized_id = "".join([capitalize(o) for o in id.split("_")])\n
    action_action = view_action_basis % (region, capitalized_id)\n
    action_condition = view_condition_basis % (capitalize(region),capitalized_id)\n
    context.addAction(id = action_id,\n
                      name = "Amortisation Details",\n
                      action = action_action,\n
                      condition = action_condition,\n
                      permission = view_permissions_basis,\n
                      category = "object_view",\n
                      visible=1)\n
    print "OK"\n
\n
print\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PortalType_ImmobilisationMovement_addAmortisationMethodActions</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
