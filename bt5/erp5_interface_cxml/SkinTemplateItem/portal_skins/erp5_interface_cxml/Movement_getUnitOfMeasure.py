default = "EA"
mapping_dict = {
  "unit/piece": "EA"
}
quanity_unit = context.getQuantityUnit()
return mapping_dict.get(quanity_unit, default)
