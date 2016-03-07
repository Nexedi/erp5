"""
  return firstname plus lastname of the owner of document if the document belong
  to a registred person in person_module otherwise it's an anonymous requester
"""
owner = context.owner_info()['id']
owner_object = context.portal_catalog.getResultValue(portal_type='Person', reference=owner)

owner_name = 'Requester'

if owner_object is not None:
   if  owner_object.getFirstName() + owner_object.getLastName() != '':
     owner_name = "%s %s" % (owner_object.getFirstName(), owner_object.getLastName())
   else:
     owner_name = owner
return owner_name
