apparel_model = context
result = ''

apparel_cloth_list = apparel_model.getValueList('specialise',portal_type=['Apparel Cloth'])
apparel_shape = apparel_model.getDefaultValue('specialise',portal_type=['Apparel Shape'])

object_list = []

if apparel_shape != None:
  object_list.append(apparel_shape)

object_list += apparel_cloth_list

for object in object_list:
  nomenclature_tmp = object.getBillOfMaterialDescription('')
  if nomenclature_tmp != '':
    result += nomenclature_tmp+'\n'

return result
