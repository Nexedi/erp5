## Script (Python) "modele_dessins_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
modele = context
forme = modele.getDefaultValue('specialise',portal_type=['Forme'])

if forme<>None:
 dessins_list1 = forme.objectValues()
else :
 dessins_list1 = []

vetements_list = modele.getValueList('specialise',portal_type=['Vetement'])

final_list = []

for dessin in dessins_list1 :
  if dessin.portal_type == 'Dessin Technique' :
    final_list.append(dessin)

for vetement in vetements_list :
  dessins_list2 = vetement.objectValues()
  for dessin in dessins_list2 :
    if dessin.portal_type == 'Dessin Technique' :
      final_list.append(dessin)

return final_list
