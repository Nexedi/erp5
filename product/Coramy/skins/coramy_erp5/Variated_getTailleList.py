## Script (Python) "Variated_getTailleList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=correspondance=None, morphologie=None
##title=
##
tailles_list = context.getTailleList()
tailles_coramy = []
tailles_client = []
for taille in tailles_list :
  taille_items = taille.split('/')
  tailles_coramy.append(taille_items[len(taille_items)-1])

if correspondance == None :
  tailles_client = tailles_coramy
else :
  if morphologie is None :
    for taille in tailles_list :
      if correspondance.getCell(None, taille, base_id='taille_client') <> None :
        tailles_client.append(correspondance.getCell(None, taille, base_id='taille_client').taille_client)
      else :
        tailles_client.append("")
  else :
    my_morphologie = context.restrictedTraverse(morphologie).getMorphoType()
    for taille in tailles_list :
      if correspondance.getCell(my_morphologie, taille, base_id='taille_client') <> None :
        tailles_client.append(correspondance.getCell(my_morphologie, taille, base_id='taille_client').taille_client)
      else :
        tailles_client.append("")

tailles = [tailles_coramy, tailles_client, tailles_list]
return tailles
