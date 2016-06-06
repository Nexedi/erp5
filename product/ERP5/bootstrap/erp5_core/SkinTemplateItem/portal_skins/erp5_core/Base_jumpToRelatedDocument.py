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
            <value> <string>from ZTUtils import make_query\n
\n
request=context.REQUEST\n
\n
form = getattr(context,form_id)\n
field = form.get_field(field_id)\n
base_category = field.get_value(\'base_category\')\n
portal_type = map(lambda x:x[0],field.get_value(\'portal_type\'))\n
kw = {}\n
for k, v in field.get_value(\'parameter_list\') :\n
  kw[k] = v\n
accessor_name = \'get%sValueList\' % \'\'.join([part.capitalize() for part in base_category.split(\'_\')])\n
jump_reference_list = getattr(context, accessor_name)(portal_type=portal_type, filter=kw)\n
\n
if len(jump_reference_list)==1:\n
  jump_reference = jump_reference_list[0]\n
  return jump_reference.Base_redirect()\n
else:\n
  selection_uid_list = map(lambda x:x.getUid(),jump_reference_list) or None\n
  kw = {\'uid\': selection_uid_list}\n
  # We need to reset the selection. Indeed, some sort columns done in another \n
  # jump could be meaningless for this particular jump. The consequence could \n
  # be an empty list\n
  context.portal_selections.setSelectionFor(\'Base_jumpToRelatedObjectList\', None)\n
  context.portal_selections.setSelectionParamsFor(\'Base_jumpToRelatedObjectList\',kw)\n
  request.set(\'object_uid\', context.getUid())\n
  request.set(\'uids\', selection_uid_list)\n
  request.set(\'original_form_id\', form_id)\n
  return context.Base_jumpToRelatedObjectList(uids=selection_uid_list, REQUEST=request)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id, field_id, selection_index=0, selection_name=\'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_jumpToRelatedDocument</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
