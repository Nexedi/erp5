## Script (Python) "getModeleAggregatedNomenclature"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
modele = context
result = ''

try:
  vetement_list = modele.getValueList('specialise',portal_type=['Vetement'])
  forme = modele.getDefaultValue('specialise',portal_type=['Forme'])
  if forme.getNomenclature('') <> '' :
    result += forme.getNomenclature('')+'\n'
  for vetement in vetement_list :
    if vetement.getNomenclature('') <> '' :
      result += vetement.getNomenclature('')+'\n'
  return result
except :
  return "Titre calculé"
