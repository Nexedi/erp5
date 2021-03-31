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
generateDomain = context.Base_generateDomain

return [
  generateDomain(parent, 'creation_date_lt2', '< 2', 'creation_date', domain_mapping_dict["< 2"]),
  generateDomain(parent, 'creation_date_2to7', '2 - 7', 'creation_date', domain_mapping_dict["2 - 7"]),
  generateDomain(parent, 'creation_date_7to30', '7 - 30', 'creation_date', domain_mapping_dict["7 - 30"]),
  generateDomain(parent, 'creation_date_gt30', '> 30', 'creation_date', domain_mapping_dict["> 30"]),
]
