allowed_insolvency_proceeding_type_for_private_customer_list = ['service_module/indebtedness']
all_processing_type = context.Ticket_getResourceItemList(portal_type='Insolvency Proceeding', include_context=False, empty_item=False)
is_person_private_customer = context.getCareerRoleValue().isMemberOf('role/customer/private')

if is_person_private_customer:
  return [processing_type for processing_type in all_processing_type if processing_type[1] in allowed_insolvency_proceeding_type_for_private_customer_list]
else:
  return [processing_type for processing_type in all_processing_type if processing_type[1] not in allowed_insolvency_proceeding_type_for_private_customer_list]
