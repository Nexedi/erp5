from DateTime import DateTime
criterion_property = "delivery.stop_date"
now = DateTime()
domain_list = []
parents_criterion_dict = {}

def appendNewTempDomain(id, criterion_dict=None, **kw):
  if criterion_dict is None:
    criterion_dict = parents_criterion_dict
  else:
    criterion_dict.update(parents_criterion_dict)
  domain = parent.generateTempDomain(id=id)
  domain.edit(
    criterion_property_list=criterion_dict.keys(),
    **kw
  )
  for property_id, criterion_kw in criterion_dict.items():
    domain.setCriterion(property_id, **criterion_kw)
  domain_list.append(domain)

appendNewTempDomain(
  id="future",
  title="Future",
  criterion_dict={criterion_property: {"min": now, "max": DateTime('9999/01/01 00:00')}},
)
appendNewTempDomain(
  id="past",
  title="Past",
  criterion_dict={criterion_property: {"min": DateTime('1000/01/01 00:00'), "max": now}},
)

return domain_list
