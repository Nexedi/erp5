brain_list = []
org_dict = {}

# Copy the address if from a company
if parameter_dict.get('relation', None):
  # this is the address of the person
  org_dict['title'] = parameter_dict['relation']
  org_dict['id'] = "%s" %(parameter_dict['id'])
#  org_dict['email'] = parameter_dict['email']

  # Check how many addresses this organisation has
  if org_dict['title'] == parameter_dict["shipping_company"]:
    address_tag_list = ['billing', 'shipping']
  else:
    address_tag_list = ['billing',]

  for address_tag in address_tag_list:
    for key in ['cellphone',
                'city',
                'country',
                'fax',
                'phone',
                'street',
                'zip',
                ]:
      org_dict["%s-%s" %(address_tag,key)] = parameter_dict.get("%s_address_%s" %(address_tag, key), '')
  org_dict['country'] = org_dict['billing-country']
  brain_list = [brain(context=context,
                        object_type=context.getDestinationObjectType(),
                        **org_dict),]

return brain_list
