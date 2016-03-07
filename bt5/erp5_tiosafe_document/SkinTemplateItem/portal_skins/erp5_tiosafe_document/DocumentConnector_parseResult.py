parser_dict = parser_dict['object'][1]
data_list = []
for dictionnary in result:
  property_dict = {}
  for k, v in dictionnary.items():
    k = parser_dict.get(k)
    if k is not None:
      k = k[0]
      if same_type(v, ""):
        property_dict[k] = unicode(v)
      else:
        property_dict[k] = v
  data_list.append(property_dict)
return data_list
