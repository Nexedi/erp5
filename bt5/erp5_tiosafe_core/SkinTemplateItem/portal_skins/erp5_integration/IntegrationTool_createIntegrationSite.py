"""
  This script creates a default integration site based on informations
  inputed by the developper.
"""

portal_object = context.getPortalObject()

# Check and create the tiosafe sync user if not exists
acl_users = portal_object.acl_users
if not acl_users.getUserById('tiosafe_sync_user'):
  acl_users.zodb_users.manage_addUser(
      user_id='tiosafe_sync_user',
      login_name='tiosafe_sync_user',
      password='tiosafe_sync_user',
      confirm='tiosafe_sync_user',
  )
  # BBB for PAS 1.9.0 we pass a response and undo the redirect
  response = container.REQUEST.RESPONSE
  acl_users.zodb_roles.manage_assignRoleToPrincipals(
      'Manager',
      ('tiosafe_sync_user',),
      RESPONSE=response)
  response.setStatus(200)

# this dict map the portal type with their type
mapping_type_dict = {
    'person_module': 'Node',
    'organisation_module': 'Node',
    'account_module': 'Node',
    'component_module': 'Resource',
    'service_module': 'Resource',
    'product_module': 'Resource',
}

# Create an integration site
integration_tool = portal_object.portal_integrations
site = integration_tool.newContent(
    portal_type="Integration Site",
    id=reference,
    title=reference.capitalize(),
    reference=reference,
    source_trade="sale_trade_condition_module/tiosafe_sale_trade_condition",
    destination_trade="purchase_trade_condition_module/tiosafe_purchase_trade_condition",
    source_carrier="service_module/tiosafe_discount_service",
    destination_carrier="service_module/tiosafe_delivery_service",
)

# create connectors
created_connector_list = []
i = 0
for connector in connector_list:
  new_connector = site.newContent(
      portal_type="Web Service Connector",
      id="%s_connector" % (connector, ),
      transport=connector,
  )
  created_connector_list.append(new_connector)

# create methods for each module that will be synchronized
base_request_name_list = ["create", "update", "delete", ]

# if it's possible define the default connector
if len(created_connector_list) == 1:
  default_connector = created_connector_list[0]
else:
  default_connector = None

# order the module list, first build the Node and the Resource and later the
# Transactions
module_list = [x.split('/')[-1] for x in module_list]
ordered_module_list = []
for module in module_list:
  if module in mapping_type_dict:
    sort_tuple = (1, (module, mapping_type_dict[module]))
  else:
    sort_tuple = (2, (module, 'Transaction'))
  ordered_module_list.append(sort_tuple)
ordered_module_list.sort()
# retrieve the list of tuple which contain the module id and the mapping type
ordered_module_list = [
    (k, v)
    for k, v in [
      y
      for x, y in ordered_module_list
    ]
]

# build each integration module with its sub object
sync_tool = portal_object.portal_synchronizations
for module_id, abstract_class_name in ordered_module_list:
  module = portal_object.restrictedTraverse(module_id)
  module_portal_type = module.getPortalType()
  module_name = module_portal_type.replace(" Module", "").replace(" ", "")

  # Create pub and sub
  pub = sync_tool.newContent(
      id="%s_%s_pub" % (reference, module_id),
      portal_type="SyncML Publication",
      title="%s_%s_pub_synchronization" % (reference, module_name),
      source_reference="%s_%s_synchronization" % (reference, module_name),
      url_string=portal_object.absolute_url(),
      source=module.getRelativeUrl(),
      conduit_module_id="erp5.component.module.ERP5%sConduit" % (abstract_class_name, ),
      list_method_id="%sModule_get%sValueList" % (module_name, module_name),
      xml_binding_generator_method_id="%s_asTioSafeXML" % (abstract_class_name, ),
      synchronization_id_generator_method_id="generateNewId",
      content_type="application/vnd.syncml+xml",
      authentification_type="syncml:auth-basic",
      authentification_format="b64",
      is_synchronized_with_erp5_portal=True,
      is_activity_enabled=True,
      gid_generator_method_id="Synchronization_getERP5ObjectGIDFromRelatedObject",
  )
  pub.validate()
  sub = sync_tool.newContent(
      id="%s_%s_sub" % (reference, module_id),
      portal_type="SyncML Subscription",
      title="%s_%s_sub_synchronization" % (reference, module_name),
      source_reference="%s_%s_synchronization_sub" % (reference, module_name),
      subscription_url_string=portal_object.absolute_url(),
      destination_reference="%s_%s_synchronization" % (reference, module_name),
      url_string=portal_object.absolute_url(),
      source=site.getRelativeUrl(),
      list_method_id=module.getId(),
      conduit_module_id="erp5.component.module.TioSafe%sConduit" % (abstract_class_name, ),
      xml_binding_generator_method_id="asXML",
      content_type="application/vnd.syncml+xml",
      synchronization_id_generator_method_id="generateNewId",
      sync_ml_alert_code="two_way",
      is_synchronized_with_erp5_portal=True,
      is_activity_enabled=True,
      user_id="tiosafe_sync_user",
      password="tiosafe_sync_user",
      gid_generator_method_id="Synchronization_getBrainGIDFromRelatedObject",
  )
  sub.validate()

  # create the integration module
  integration_module = site.newContent(
      portal_type="Integration Module",
      id=module_id,
      title=module_name,
      int_index=i,
      source_section_value=pub,
      destination_section_value=sub,
  )
  i += 1

  # Create the generic Web Service Request which render module element list and
  # which check the gid consitency for the module
  integration_module.newContent(
      portal_type="Web Service Request",
      id="checkDataConsistency",
      title="Check data integrity of %s" % (module_name, ),
      reference="check%sDataIntegrity" % (module_name, ),
      source_value=default_connector,
  )
  integration_module.newContent(
      portal_type="Web Service Request",
      id="getObjectList",
      title="Get %s" % (module_portal_type.replace(" Module", "").capitalize(), ),
      reference="get%sList" % (module_name, ),
      source_value=default_connector,
      brain_class_file='TioSafeBrain',
      brain_class_name=abstract_class_name,
      destination_object_type=module_name,
  )

  # browse allowed content type to creates methods
  for allowed_type in module.allowedContentTypes():
    allowed_type_name = allowed_type.getTitle().replace(" ", "",)
    for base_request_name in base_request_name_list:
      integration_module.newContent(
          portal_type="Web Service Request",
          id="%s%s" % (base_request_name, allowed_type_name),
          title="%s %s" % (base_request_name.capitalize(), allowed_type.getTitle().capitalize()),
          source_value=default_connector,
      )

    # handle specific cases
    if allowed_type_name in ["Person", "Organisation"]:
      # first method to get sub object:
      integration_module.newContent(
          portal_type="Web Service Request",
          id="%s_getAddressList" % (allowed_type_name),
          title="Get Address",
          source_value=default_connector,
      )
      # then method to update/delete/create
      for base_request_name in base_request_name_list:
        integration_module.newContent(
            portal_type="Web Service Request",
            id="%sAddress" % (base_request_name),
            title="%s Address" % (base_request_name.capitalize(), ),
            source_value=default_connector,
        )
    elif allowed_type_name in ["SaleOrder", "PurchaseOrder"]:
      # method to get lines
      integration_module.newContent(
          portal_type="Web Service Request",
          id="%s_get%sLineList" % (allowed_type_name, allowed_type_name),
          title="Get %s Line" % (allowed_type.getTitle().capitalize(), ),
          source_value=default_connector,
      )

message = context.Base_translateString("Integration Site created.")
return site.Base_redirect(keep_items=dict(portal_status_message=message))
