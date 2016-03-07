main_name = "%s %s" %(parameter_dict['firstname'], parameter_dict['lastname'])
first_person_dict = {}
site = context.getIntegrationSite()

# First person dict
for key in ['firstname',
            'lastname',
            'is_customer',
            'email',
            'id',
            ]:
  first_person_dict[key] = "%s" %(parameter_dict.get(key,''),)
# Copy the address if not from a company
if not parameter_dict.get('relation', None):
  # this is the address of the person
  for key in ['cellphone',
              'phone',
              'fax',
              'city',
              'country',
              'street',
              'zip',
              ]:
    first_person_dict["billing-%s" %key] = parameter_dict.get("billing_address_%s" %key, '')
  first_person_dict['relation'] = ''
else:
  # Find the gid of the relation
  gid_prefix = context.getParentValue().organisation_module.getGidPrefix("")
  gid_property_list = context.getParentValue().organisation_module.getGidPropertyList()
  gid = [gid_prefix,]
  for prop in gid_property_list:
    if prop == "title":
      gid.append(parameter_dict['relation'])
    elif prop == "country":
      region = site.getCategoryFromMapping(category = 'Country/%s' % parameter_dict['billing_address_country'],
                                           create_mapping=True,
                                           create_mapping_line=True,
                                           ).split('/', 1)[-1]
      gid.append(region)
    elif prop == "email":
      gid.append(parameter_dict['email'])
  gid = " ".join(gid)
  first_person_dict['relation'] = gid

brain_list = [brain(context=context,
                    object_type=context.getDestinationObjectType(),
                    **first_person_dict),]

return brain_list
