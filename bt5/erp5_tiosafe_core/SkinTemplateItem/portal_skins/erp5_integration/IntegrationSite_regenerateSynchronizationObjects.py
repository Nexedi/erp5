portal_object = context.getPortalObject()

sync_tool = portal_object.portal_synchronizations

# Check and create the tiosafe sync user if not exists
acl_users = portal_object.acl_users
if not acl_users.getUserById('tiosafe_sync_user'):
  acl_users.zodb_users.manage_addUser(
      user_id='tiosafe_sync_user',
      login_name='tiosafe_sync_user',
      password='tiosafe_sync_user',
      confirm='tiosafe_sync_user',
  )
  acl_users.zodb_roles.manage_assignRoleToPrincipals(
      'Manager',
      ('tiosafe_sync_user',))

node_list = ['person_module', 'organisation_module']
resource_list = ['product_module',]

site = context
reference = site.getReference()

for module in context.objectValues(portal_type="Integration Module"):

  if module.getId() in node_list:
    abstract_class_name = "Node"
  elif module.getId() in resource_list:
    abstract_class_name = "Resource"
  else:
    abstract_class_name = "Transaction"

  module_type = module.getId().replace('_module', '').replace('_', '').capitalize()

  # Create pub and sub
  module_name = module.getId()
  pub = sync_tool.newContent(id="%s_%s_pub" %(reference, module_name),
                             portal_type="SyncML Publication",
                             title="%s_%s_pub_synchronization" %(reference, module_name),
                             source_reference="%s_%s_synchronization" %(reference, module_name),
                             url_string=portal_object.absolute_url(),
                             source=module.getRelativeUrl(),
                             conduit_module_id="erp5.component.module.ERP5%sConduit" %(abstract_class_name,),
                             list_method_id="%sModule_get%sValueList"% (module_type, module_type),
                             xml_binding_generator_method_id="%s_asTioSafeXML" %(abstract_class_name,),
                             synchronization_id_generator_method_id="generateNewId",
                             content_type="application/vnd.syncml+xml",
                             authentification_type="syncml:auth-basic",
                             authentification_format="b64",
                             is_synchronized_with_erp5_portal=True,
                             is_activity_enabled=True,
                             gid_generator_method_id="Synchronization_getERP5ObjectGIDFromRelatedObject",
                             )
  pub.validate()
  sub = sync_tool.newContent(id="%s_%s_sub" %(reference, module_name),
                             portal_type="SyncML Subscription",
                             title="%s_%s_sub_synchronization" %(reference, module_name),
                             source_reference="%s_%s_synchronization_sub" %(reference, module_name),
                             subscription_url_string=portal_object.absolute_url(),
                             destination_reference="%s_%s_synchronization" %(reference, module_name),
                             url_string=portal_object.absolute_url(),
                             source=site.getRelativeUrl(),
                             list_method_id=module.getId(),
                             conduit_module_id="erp5.component.module.TioSafe%sConduit" %(abstract_class_name,),
                             xml_binding_generator_method_id="asXML",
                             content_type="application/vnd.syncml+xml",
                             synchronization_id_generator_method_id="generateNewId",
                             sync_ml_alert_code="two_way",
                             is_synchronized_with_erp5_portal=True,
                             is_activity_enabled=True,
                             user_id='tiosafe_sync_user',
                             password='tiosafe_sync_user',
                             gid_generator_method_id="Synchronization_getBrainGIDFromRelatedObject",
                             )
  sub.validate()

  module.edit(source_section_value=pub,
              destination_section_value=sub)



message = context.Base_translateString("Synchronization objects recreated.")
return site.Base_redirect(keep_items=dict(portal_status_message=message))
