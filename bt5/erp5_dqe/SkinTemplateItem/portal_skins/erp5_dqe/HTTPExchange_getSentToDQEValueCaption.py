from six.moves import urllib

resource_value = context.getResourceValue()
if not resource_value.isMemberOf('http_exchange_resource/dqe'):
  return ''

request = context.getRequest()
if not request:
  return ''
query_dict = urllib.urlparse.parse_qs(urllib.urlparse.urlparse(request).query)
dqe_resource_category = context.getPortalObject().portal_categories.http_exchange_resource.dqe
service_value_to_key_list_dict = {
  dqe_resource_category.DefaultEmail: ('Email', ),
  dqe_resource_category.DefaultTelephone: ('Tel', 'Pays'),
  dqe_resource_category.MobileTelephone: ('Tel', 'Pays'),
  dqe_resource_category.DefaultAddress: ('Adresse', 'Pays'),
  dqe_resource_category.DeliveryAddress: ('Adresse', 'Pays'),
  dqe_resource_category.OrganisationData: ('Siret', ),
  dqe_resource_category.RelocationData: ('Adresse', 'CodePostal', 'Ville', 'Complement', 'LieuDit'),
}

sent_value_list = []

for key in service_value_to_key_list_dict[resource_value]:
  value_list = query_dict.get(key, [])
  if resource_value in (
    dqe_resource_category.DefaultAddress, dqe_resource_category.DeliveryAddress
  ) and key == 'Adresse' and value_list:
    value_list = [x for x in value_list[0].split('|') if x]
  if value_list:
    sent_value_list += value_list
return ', '.join(sent_value_list)
