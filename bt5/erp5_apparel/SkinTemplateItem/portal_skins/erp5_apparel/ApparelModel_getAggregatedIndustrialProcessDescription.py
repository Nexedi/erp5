apparel_model = context
result = ''

apparel_cloth_list = apparel_model.getValueList('specialise',portal_type=['Apparel Cloth'])
apparel_shape = apparel_model.getDefaultValue('specialise',portal_type=['Apparel Shape'])

object_list = []

if apparel_shape != None:
  object_list.append(apparel_shape)

object_list += apparel_cloth_list

for object in object_list:
  procedure_tmp = object.getIndustrialProcessDescription('')
  if procedure_tmp != '':
    result += procedure_tmp+'\n'

return result
