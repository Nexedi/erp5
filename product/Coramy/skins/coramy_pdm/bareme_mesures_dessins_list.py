## Script (Python) "bareme_mesures_dessins_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=correspondance_mesures
##title=
##
modele = context
forme = modele.getDefaultValue('specialise',portal_type=['Forme'])
dessins_list = []
dessins_final_list = []

if forme<>None:
 dessins_list += forme.contentValues(filter={'portal_type':'Dessin Technique'})
 if len(dessins_list) == 1 :
   dessins_final_list = dessins_list
 else :
   for dessin in dessins_list :
     if dessin.getId().find('fl') == (-1) and dessin.getId().find('mes') == (-1) and dessin.getId().find('typ') == (-1):
       dessins_final_list = [dessin]
if len(dessins_final_list) == 0 :
  dessins_final_list = [None]

vetements_list = modele.getValueList('specialise',portal_type=['Vetement'])
for vetement in vetements_list :
  vetement_dessins_list =[]
  # TEMPORARY modification because contentValues does not work in all cases
  #  dessins_list = vetement.contentValues(filter={'portal_type':'Dessin Technique'})
  dessins_list = []
  raw_dessins_list = vetement.objectValues()
  for dessin_item in raw_dessins_list :
    if dessin_item.getPortalType() == 'Dessin Technique' :
      dessins_list.append(dessin_item)

  if len(dessins_list) == 1 and dessins_list[0].getId().find('fl') == (-1) and dessins_list[0].getId().find('typ') == (-1):
    vetement_dessins_list = dessins_list
  else :
    for dessin in dessins_list :
      if dessin.getId().find('fl') == (-1) and dessin.getId().find('typ') == (-1) :
        vetement_dessins_list = [dessin]

  correspondance = vetement.getDefaultValue('specialise',portal_type=['Correspondance Mesures'])
  if correspondance <> None and len(vetement_dessins_list) == 0 :
    vetement_dessins_list.append(correspondance)
  dessins_final_list += vetement_dessins_list

if correspondance_mesures<>None :
  dessins_final_list.append(correspondance_mesures)

if len(dessins_final_list) == 1 :
  dessins_final_list += [None]

return dessins_final_list
