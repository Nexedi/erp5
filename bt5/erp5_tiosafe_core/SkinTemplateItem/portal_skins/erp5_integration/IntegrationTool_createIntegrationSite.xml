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
  This script creates a default integration site based on informations\n
  inputed by the developper.\n
"""\n
\n
portal_object = context.getPortalObject()\n
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
# this dict map the portal type with their type\n
mapping_type_dict = {\n
    \'person_module\': \'Node\',\n
    \'organisation_module\': \'Node\',\n
    \'account_module\': \'Node\',\n
    \'component_module\': \'Resource\',\n
    \'service_module\': \'Resource\',\n
    \'product_module\': \'Resource\',\n
}\n
\n
# Create an integration site\n
integration_tool = portal_object.portal_integrations\n
site = integration_tool.newContent(\n
    portal_type="Integration Site",\n
    id=reference,\n
    title=reference.capitalize(),\n
    reference=reference,\n
    source_trade="sale_trade_condition_module/tiosafe_sale_trade_condition",\n
    destination_trade="purchase_trade_condition_module/tiosafe_purchase_trade_condition",\n
    source_carrier="service_module/tiosafe_discount_service",\n
    destination_carrier="service_module/tiosafe_delivery_service",\n
)\n
\n
# create connectors\n
created_connector_list = []\n
i = 0\n
for connector in connector_list:\n
  new_connector = site.newContent(\n
      portal_type="Web Service Connector",\n
      id="%s_connector" % (connector, ),\n
      transport=connector,\n
  )\n
  created_connector_list.append(new_connector)\n
\n
# create methods for each module that will be synchronized\n
base_request_name_list = ["create", "update", "delete", ]\n
\n
# if it\'s possible define the default connector\n
if len(created_connector_list) == 1:\n
  default_connector = created_connector_list[0]\n
else:\n
  default_connector = None\n
\n
# order the module list, first build the Node and the Resource and later the\n
# Transactions\n
module_list = [x.split(\'/\')[-1] for x in module_list]\n
ordered_module_list = []\n
for module in module_list:\n
  if module in mapping_type_dict:\n
    sort_tuple = (1, (module, mapping_type_dict[module]))\n
  else:\n
    sort_tuple = (2, (module, \'Transaction\'))\n
  ordered_module_list.append(sort_tuple)\n
ordered_module_list.sort()\n
# retrieve the list of tuple which contain the module id and the mapping type\n
ordered_module_list = [\n
    (k, v)\n
    for k, v in [\n
      y\n
      for x, y in ordered_module_list\n
    ]\n
]\n
\n
# build each integration module with its sub object\n
sync_tool = portal_object.portal_synchronizations\n
for module_id, abstract_class_name in ordered_module_list:\n
  module = portal_object.restrictedTraverse(module_id)\n
  module_portal_type = module.getPortalType()\n
  module_name = module_portal_type.replace(" Module", "").replace(" ", "")\n
\n
  # Create pub and sub\n
  pub = sync_tool.newContent(\n
      id="%s_%s_pub" % (reference, module_id),\n
      portal_type="SyncML Publication",\n
      title="%s_%s_pub_synchronization" % (reference, module_name),\n
      source_reference="%s_%s_synchronization" % (reference, module_name),\n
      url_string=portal_object.absolute_url(),\n
      source=module.getRelativeUrl(),\n
      conduit_module_id="Products.ERP5TioSafe.Conduit.ERP5%sConduit" % (abstract_class_name, ),\n
      list_method_id="%sModule_get%sValueList" % (module_name, module_name),\n
      xml_binding_generator_method_id="%s_asTioSafeXML" % (abstract_class_name, ),\n
      synchronization_id_generator_method_id="generateNewId",\n
      content_type="application/vnd.syncml+xml",\n
      authentification_type="syncml:auth-basic",\n
      authentification_format="b64",\n
      is_synchronized_with_erp5_portal=True,\n
      is_activity_enabled=True,\n
      gid_generator_method_id="Synchronization_getERP5ObjectGIDFromRelatedObject",\n
  )\n
  pub.validate()\n
  sub = sync_tool.newContent(\n
      id="%s_%s_sub" % (reference, module_id),\n
      portal_type="SyncML Subscription",\n
      title="%s_%s_sub_synchronization" % (reference, module_name),\n
      source_reference="%s_%s_synchronization_sub" % (reference, module_name),\n
      subscription_url_string=portal_object.absolute_url(),\n
      destination_reference="%s_%s_synchronization" % (reference, module_name),\n
      url_string=portal_object.absolute_url(),\n
      source=site.getRelativeUrl(),\n
      list_method_id=module.getId(),\n
      conduit_module_id="Products.ERP5TioSafe.Conduit.TioSafe%sConduit" % (abstract_class_name, ),\n
      xml_binding_generator_method_id="asXML",\n
      content_type="application/vnd.syncml+xml",\n
      synchronization_id_generator_method_id="generateNewId",\n
      sync_ml_alert_code="two_way",\n
      is_synchronized_with_erp5_portal=True,\n
      is_activity_enabled=True,\n
      user_id="tiosafe_sync_user",\n
      password="tiosafe_sync_user",\n
      gid_generator_method_id="Synchronization_getBrainGIDFromRelatedObject",\n
  )\n
  sub.validate()\n
\n
  # create the integration module\n
  integration_module = site.newContent(\n
      portal_type="Integration Module",\n
      id=module_id,\n
      title=module_name,\n
      int_index=i,\n
      source_section_value=pub,\n
      destination_section_value=sub,\n
  )\n
  i += 1\n
\n
  # Create the generic Web Service Request which render module element list and\n
  # which check the gid consitency for the module\n
  integration_module.newContent(\n
      portal_type="Web Service Request",\n
      id="checkDataConsistency",\n
      title="Check data integrity of %s" % (module_name, ),\n
      reference="check%sDataIntegrity" % (module_name, ),\n
      source_value=default_connector,\n
  )\n
  integration_module.newContent(\n
      portal_type="Web Service Request",\n
      id="getObjectList",\n
      title="Get %s" % (module_portal_type.replace(" Module", "").capitalize(), ),\n
      reference="get%sList" % (module_name, ),\n
      source_value=default_connector,\n
      brain_class_file=\'TioSafeBrain\',\n
      brain_class_name=abstract_class_name,\n
      destination_object_type=module_name,\n
  )\n
\n
  # browse allowed content type to creates methods\n
  for allowed_type in module.allowedContentTypes():\n
    allowed_type_name = allowed_type.getTitle().replace(" ", "",)\n
    for base_request_name in base_request_name_list:\n
      integration_module.newContent(\n
          portal_type="Web Service Request",\n
          id="%s%s" % (base_request_name, allowed_type_name),\n
          title="%s %s" % (base_request_name.capitalize(), allowed_type.getTitle().capitalize()),\n
          source_value=default_connector,\n
      )\n
\n
    # handle specific cases\n
    if allowed_type_name in ["Person", "Organisation"]:\n
      # first method to get sub object:\n
      integration_module.newContent(\n
          portal_type="Web Service Request",\n
          id="%s_getAddressList" % (allowed_type_name),\n
          title="Get Address",\n
          source_value=default_connector,\n
      )\n
      # then method to update/delete/create\n
      for base_request_name in base_request_name_list:\n
        integration_module.newContent(\n
            portal_type="Web Service Request",\n
            id="%sAddress" % (base_request_name),\n
            title="%s Address" % (base_request_name.capitalize(), ),\n
            source_value=default_connector,\n
        )\n
    elif allowed_type_name in ["SaleOrder", "PurchaseOrder"]:\n
      # method to get lines\n
      integration_module.newContent(\n
          portal_type="Web Service Request",\n
          id="%s_get%sLineList" % (allowed_type_name, allowed_type_name),\n
          title="Get %s Line" % (allowed_type.getTitle().capitalize(), ),\n
          source_value=default_connector,\n
      )\n
\n
message = context.Base_translateString("Integration Site created.")\n
return site.Base_redirect(keep_items=dict(portal_status_message=message))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference, connector_list, module_list, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationTool_createIntegrationSite</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
