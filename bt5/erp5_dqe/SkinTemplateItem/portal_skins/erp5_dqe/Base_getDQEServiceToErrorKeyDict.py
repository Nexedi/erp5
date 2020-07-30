'''
  DQE API returns the result code in different key for different calls.
  This is a utility script doing the mapping
'''
dqe_resource_category = context.getPortalObject().portal_categories.http_exchange_resource.dqe
return {
  dqe_resource_category.DefaultEmail: 'IdError',
  dqe_resource_category.DefaultTelephone: 'IdError',
  dqe_resource_category.MobileTelephone: 'IdError',
  dqe_resource_category.DefaultAddress: 'DQECodeDetail',
  dqe_resource_category.DeliveryAddress: 'DQECodeDetail',
  dqe_resource_category.OrganisationData: 'DQE_status',
}
