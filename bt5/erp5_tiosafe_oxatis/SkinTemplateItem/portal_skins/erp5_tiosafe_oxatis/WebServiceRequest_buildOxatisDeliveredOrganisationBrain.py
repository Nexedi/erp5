brain_list = []
org_dict = {}

if len(parameter_dict.get('shipping_company', '')) and  \
       parameter_dict['shipping_company'] != parameter_dict.get('relation', ''):
  org_dict["title"] = parameter_dict['shipping_company']
  org_dict['id'] = "%s" %(parameter_dict['id'])
#  org_dict["email"] = "%s" %(parameter_dict['email'],)
  for key in ['cellphone',
              'city',
              'country',
              'fax',
              'phone',
              'street',
              'zip',
              ]:
    org_dict["shipping-%s" %key] = parameter_dict.get("shipping_address_%s" %key, None)

  org_dict["country"] = org_dict["shipping-country"]
  brain_list = [brain(context=context,
                      object_type=context.getDestinationObjectType(),
                      **org_dict),]

return brain_list
