so_dict = parameter_dict.copy()

billing_user = "%s %s" %(parameter_dict['billing_firstname'], parameter_dict['billing_lastname'])
site = context.getIntegrationSite()

# Compute the gid the main user
gid_prefix = context.getParentValue().person_module.getGidPrefix("")
gid_property_list = context.getParentValue().person_module.getGidPropertyList()
person_gid = [gid_prefix,]
for prop in gid_property_list:
  if prop == "firstname":
    person_gid.append(parameter_dict['billing_firstname'])
  elif prop == "lastname":
    person_gid.append(parameter_dict['billing_lastname'])
  elif prop == "email":
    person_gid.append(parameter_dict['user_email'])
person_gid = " ".join(person_gid)

# First the invoice part
if parameter_dict.get("billing_company", None):
  # We have an organisation, compute its GID
  gid_prefix = context.getParentValue().organisation_module.getGidPrefix("")
  gid_property_list = context.getParentValue().organisation_module.getGidPropertyList()
  gid = [gid_prefix,]
  for prop in gid_property_list:
    if prop == "title":
      gid.append(parameter_dict['billing_company'])
    elif prop == "country":
      region = site.getCategoryFromMapping(category = 'Country/%s' % parameter_dict['billing_address_country'],
                                           create_mapping=True,
                                           create_mapping_line=True,
                                           ).split('/', 1)[-1]
      gid.append(region)
    elif prop == "email":
      gid.append(parameter_dict['user_email'])
  gid = " ".join(gid)
  so_dict['destination_administration'] = gid
  so_dict['destination_ownership'] = gid
  so_dict['destination_decision'] = person_gid
else:
  # We have the person
  so_dict['destination_administration'] = person_gid
  so_dict['destination_ownership'] = person_gid
  so_dict['destination_decision'] = person_gid

# Then the shipping part
if parameter_dict.get("shipping_company", None):
  # We have an organisation, compute its GID
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
      gid.append(parameter_dict['user_email'])
  gid = " ".join(gid)
  so_dict['destination'] = gid
else:
  # We have a person, compute his GID
  gid_prefix = context.getParentValue().delivered_person_module.getGidPrefix("")
  gid_property_list = context.getParentValue().delivered_person_module.getGidPropertyList()
  person_gid = [gid_prefix,]
  for prop in gid_property_list:
    if prop == "firstname":
      person_gid.append(parameter_dict['shipping_firstname'])
    elif prop == "lastname":
      person_gid.append(parameter_dict['shipping_lastname'])
    elif prop == "email":
      person_gid.append(parameter_dict['user_email'])
  person_gid = " ".join(person_gid)
  so_dict['destination'] = person_gid

brain_list = [brain(context=context,
                    object_type=context.getDestinationObjectType(),
                    **so_dict),]

return brain_list
