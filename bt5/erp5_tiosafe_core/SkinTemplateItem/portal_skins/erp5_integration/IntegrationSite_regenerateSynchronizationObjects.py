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
            <value> <string>portal_object = context.getPortalObject()\n
\n
sync_tool = portal_object.portal_synchronizations\n
\n
# Check and create the tiosafe sync user if not exists\n
acl_users = portal_object.acl_users\n
if not acl_users.getUserById(\'tiosafe_sync_user\'):\n
  acl_users.zodb_users.manage_addUser(\n
      user_id=\'tiosafe_sync_user\',\n
      login_name=\'tiosafe_sync_user\',\n
      password=\'tiosafe_sync_user\',\n
      confirm=\'tiosafe_sync_user\',\n
  )\n
  acl_users.zodb_roles.assignRoleToPrincipal(\'Manager\', \'tiosafe_sync_user\')\n
\n
node_list = [\'person_module\', \'organisation_module\']\n
resource_list = [\'product_module\',]\n
\n
site = context\n
reference = site.getReference()\n
\n
for module in context.objectValues(portal_type="Integration Module"):\n
\n
  if module.getId() in node_list:\n
    abstract_class_name = "Node"\n
  elif module.getId() in resource_list:\n
    abstract_class_name = "Resource"\n
  else:\n
    abstract_class_name = "Transaction"\n
\n
  module_type = module.getId().replace(\'_module\', \'\').replace(\'_\', \'\').capitalize()\n
\n
  # Create pub and sub\n
  module_name = module.getId()\n
  pub = sync_tool.newContent(id="%s_%s_pub" %(reference, module_name),\n
                             portal_type="SyncML Publication",\n
                             title="%s_%s_pub_synchronization" %(reference, module_name),\n
                             source_reference="%s_%s_synchronization" %(reference, module_name),\n
                             url_string=portal_object.absolute_url(),\n
                             source=module.getRelativeUrl(),\n
                             conduit_module_id="Products.ERP5TioSafe.Conduit.ERP5%sConduit" %(abstract_class_name,),\n
                             list_method_id="%sModule_get%sValueList"% (module_type, module_type),\n
                             xml_binding_generator_method_id="%s_asTioSafeXML" %(abstract_class_name,),\n
                             synchronization_id_generator_method_id="generateNewId",\n
                             content_type="application/vnd.syncml+xml",\n
                             authentification_type="syncml:auth-basic",\n
                             authentification_format="b64",\n
                             is_synchronized_with_erp5_portal=True,\n
                             is_activity_enabled=True,\n
                             gid_generator_method_id="Synchronization_getERP5ObjectGIDFromRelatedObject",\n
                             )\n
  pub.validate()\n
  sub = sync_tool.newContent(id="%s_%s_sub" %(reference, module_name),\n
                             portal_type="SyncML Subscription",\n
                             title="%s_%s_sub_synchronization" %(reference, module_name),\n
                             source_reference="%s_%s_synchronization_sub" %(reference, module_name),\n
                             subscription_url_string=portal_object.absolute_url(),\n
                             destination_reference="%s_%s_synchronization" %(reference, module_name),\n
                             url_string=portal_object.absolute_url(),\n
                             source=site.getRelativeUrl(),\n
                             list_method_id=module.getId(),\n
                             conduit_module_id="Products.ERP5TioSafe.Conduit.TioSafe%sConduit" %(abstract_class_name,),\n
                             xml_binding_generator_method_id="asXML",\n
                             content_type="application/vnd.syncml+xml",\n
                             synchronization_id_generator_method_id="generateNewId",\n
                             sync_ml_alert_code="two_way",\n
                             is_synchronized_with_erp5_portal=True,\n
                             is_activity_enabled=True,\n
                             user_id=\'tiosafe_sync_user\',\n
                             password=\'tiosafe_sync_user\',\n
                             gid_generator_method_id="Synchronization_getBrainGIDFromRelatedObject",\n
                             )\n
  sub.validate()\n
\n
  module.edit(source_section_value=pub,\n
              destination_section_value=sub)\n
\n
\n
\n
message = context.Base_translateString("Synchronization objects recreated.")\n
return site.Base_redirect(keep_items=dict(portal_status_message=message))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationSite_regenerateSynchronizationObjects</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
