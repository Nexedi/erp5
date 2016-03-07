main_name = "%s %s" %(parameter_dict['firstname'], parameter_dict['lastname'])
shipping_name = "%s %s" %(parameter_dict.get('shipping_firstname', ''), parameter_dict.get('shipping_lastname', ''))

person_dict = {}


if len(shipping_name.strip()) and main_name != shipping_name:
  site = context.getIntegrationSite()
  # This is another person
  person_dict['id'] = "%s" %(parameter_dict['id'])
  person_dict["is_customer"] = parameter_dict.get('is_customer', 'false')
  person_dict["firstname"] = "%s" %(parameter_dict['shipping_firstname'],)
  person_dict["lastname"] = "%s" %(parameter_dict['shipping_lastname'],)
  person_dict["email"] = "%s" %(parameter_dict['email'],)
  if parameter_dict.get('shipping_company', None):
    # Find the gid of the relation
    gid_prefix = context.getParentValue().delivered_organisation_module.getGidPrefix("")
    gid_property_list = context.getParentValue().delivered_organisation_module.getGidPropertyList()
    gid = [gid_prefix,]
    for prop in gid_property_list:
      if prop == "title":
        gid.append(parameter_dict['shipping_company'])
      elif prop == "country":
        region = site.getCategoryFromMapping(category = 'Country/%s' % parameter_dict['shipping_address_country'],
                                             create_mapping=True,
                                             create_mapping_line=True,
                                             ).split('/', 1)[-1]
        gid.append(region)
      elif prop == "email":
        gid.append(parameter_dict['email'])
    gid = " ".join(gid)
    person_dict["relation"] = gid
  else:
    for key in ['cellphone',
                'city',
                'country',
                'fax',
                'phone',
                'street',
                'zip',
                ]:
      if parameter_dict.has_key("shipping_address_%s" %key):
        person_dict["shipping-%s" %key] = parameter_dict["shipping_address_%s" %key]

  context.log("person_dict", person_dict)
  brain_list = [brain(context=context,
                    object_type=context.getDestinationObjectType(),
                    **person_dict),]

  return brain_list
else:
  return []
