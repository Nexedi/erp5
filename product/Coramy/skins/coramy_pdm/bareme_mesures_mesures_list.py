## Script (Python) "bareme_mesures_mesures_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=tailles_list=[], correspondance=None
##title=
##
vetement = context
tailles_list = tailles_list
mesures_list = vetement.getMesureVetementList()
final_mesures_list = []

# identification de la correspondance mesures à utiliser
# si pas de correspondance associée au modèle, on regarde s'il y en a une sur le vetement
if correspondance == None :
  correspondance = vetement.getDefaultValue('specialise',portal_type=['Correspondance Mesures'])

def category_property(category, property):
  if category <> None :
    if hasattr(category,property) :
      return getattr(category,property)
    else : 
      return " "
  else :
    return " "

for mesure in mesures_list :
  category_items = mesure.split("/")
  category_mesure = context.portal_categories.mesure_vetement
  for item in category_items :
    category_mesure=category_mesure[item]
  mesure_line = []

  # Gestion du code mesure
  if correspondance <> None :
    if correspondance.getCell(mesure, 'Code_mesure', base_id='mesure_client') <> None :
      mesure_line.append(correspondance.getCell(mesure, 'Code_mesure', base_id='mesure_client').mesure_client)
    else :
      # recup du code associé à la categorie
      mesure_line.append(category_property(category_mesure,"code_mesure"))
  else :
    # recup du code associé à la categorie
    mesure_line.append(category_property(category_mesure,"code_mesure"))

  # Gestion du libellé mesure
  if correspondance <> None :
    if correspondance.getCell(mesure, 'Libelle', base_id='mesure_client') <> None :
      mesure_line.append(correspondance.getCell(mesure, 'Libelle', base_id='mesure_client').mesure_client)
    else :
      # recup du titre de la categorie
      mesure_line.append(category_property(category_mesure,"title"))
  else :
    # recup du titre de la categorie
    mesure_line.append(category_property(category_mesure,"title"))

  # Gestion des mesures par tailles
  mesure_line_list = []
  for taille in tailles_list :
    if vetement.getCell(mesure, taille, base_id='mesure_coramy') <> None :
      mesure_line_list.append("&nbsp;"+str(vetement.getCell(mesure, taille, base_id='mesure_coramy').mesure_coramy)+"&nbsp;")
    else :
      mesure_line_list.append("&nbsp;")
  mesure_line.append(mesure_line_list)

  # Gestion des tolérances
  mesure_line.append(category_property(category_mesure,"tolerance"))

  final_mesures_list.append(mesure_line)

return final_mesures_list
