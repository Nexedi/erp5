if context.getParentValue().portal_type == 'Credential Request':
  return {'Address': dict(organisation_default_address='Organisation Default Address')}
return {}
