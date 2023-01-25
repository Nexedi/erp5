if depth != 0:
  return []

request = context.REQUEST
object_path = request.get('object_path')
if object_path is None:
  # Sometimes the object_path not comes with the request, when you edit for example.
  object_path = request.get('URL1').split('/')[-1]


def display_method(doc):
  return doc.getTitle()

domain_list = []
organisation =  context.organisation_module.restrictedTraverse(object_path)
for person in sorted(
      organisation.getSubordinationRelatedValueList(portal_type='Person', checked_permission='View'),
      key=display_method):
  domain = parent.generateTempDomain(id=person.getId())
  domain.edit(title = display_method(person),
              membership_criterion_base_category = ('source', 'destination'),
              membership_criterion_category = (person.getRelativeUrl(),),
              domain_generator_method_id = script.id,
              uid = person.getUid())

  domain_list.append(domain)

return domain_list
