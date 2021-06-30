def generateDomain(id, title, criterion_property, criterion_identity):
  domain = parent.generateTempDomain(id=id)
  domain.edit(title=title,
              criterion_property_list=criterion_property)
  for criterion in criterion_property:
    domain.setCriterion(criterion, criterion_identity)
  return domain

now = DateTime()

domain_mapping_dict = {
  '< 2': {
    "range": "min",
    "query": (now - 2).earliestTime()
  },
  '2 - 7': {
    "range": "minmax",
    "query": ((now - 7).earliestTime(), (now - 2).latestTime())
  },
  '7 - 30': {
    "range": "minmax",
    "query": ((now - 30).earliestTime(), (now - 7).latestTime())
  },
  '> 30': {
    "range": "max",
    "query": ((now - 30).earliestTime())
  }
}

return [
  # XXX how to build dinamically by modification_date, creation_date, delivery.start_date?
  generateDomain('modification_date_lt2', '[Modification Date] < 2', ['modification_date',], domain_mapping_dict["< 2"]),
  generateDomain('modification_date_2to7', '[Modification Date] 2 - 7', ['modification_date',], domain_mapping_dict["2 - 7"]),
  generateDomain('modification_date_7to30', '[Modification Date] 7 - 30', ['modification_date',], domain_mapping_dict["7 - 30"]),
  generateDomain('modification_date_gt30', '[Modification Date] > 30', ['modification_date',], domain_mapping_dict["> 30"]),

  generateDomain('creation_date_lt2', '[Creation Date] < 2', ['creation_date',], domain_mapping_dict["< 2"]),
  generateDomain('creation_date_2to7', '[Creation Date] 2 - 7', ['creation_date',], domain_mapping_dict["2 - 7"]),
  generateDomain('creation_date_7to30', '[Creation Date] 7 - 30', ['creation_date',], domain_mapping_dict["7 - 30"]),
  generateDomain('creation_date_gt30', '[Creation Date] > 30', ['creation_date',], domain_mapping_dict["> 30"]),

  generateDomain('delivery_start_date_lt2', '[Start Date] < 2', ['delivery.start_date',], domain_mapping_dict["< 2"]),
  generateDomain('delivery_start_date_2to7', '[Start Date]  2 - 7', ['delivery.start_date',], domain_mapping_dict["2 - 7"]),
  generateDomain('delivery_start_date_7to30', '[Start Date] 7 - 30', ['delivery.start_date',], domain_mapping_dict["7 - 30"]),
  generateDomain('delivery_start_date_gt30', '[Start Date] > 30', ['delivery.start_date',], domain_mapping_dict["> 30"]),
]
