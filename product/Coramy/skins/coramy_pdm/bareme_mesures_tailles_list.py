## Script (Python) "bareme_mesures_tailles_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=correspondance=None
##title=
##
vetement = context
tailles_list = vetement.getTailleList()
tailles_coramy = []
tailles_client = []
for taille in tailles_list :
  taille_items = taille.split('/')
  tailles_coramy.append(taille_items[len(taille_items)-1])

if correspondance == None :
  tailles_client = tailles_coramy
else :
  for taille in tailles_list :
    if correspondance.getCell(None, taille, base_id='taille_client') <> None :
      tailles_client.append(correspondance.getCell(None, taille, base_id='taille_client').taille_client)
    else :
      tailles_client.append("")

tailles = [tailles_coramy, tailles_client, tailles_list]
return tailles
