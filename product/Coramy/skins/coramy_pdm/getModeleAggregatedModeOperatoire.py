## Script (Python) "getModeleAggregatedModeOperatoire"
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
  if forme.getModeOperatoire('') <> '' :
    result += forme.getModeOperatoire('')+'\n'
  for vetement in vetement_list :
    if vetement.getModeOperatoire('') <> '' :
      result += vetement.getModeOperatoire('')+'\n'
  return result
except :
  return "Titre calculé"
