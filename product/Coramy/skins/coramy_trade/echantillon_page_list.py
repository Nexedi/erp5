## Script (Python) "echantillon_page_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ordered_lines_list, on_page
##title=
##
result = []
compteur = 0
nb_trous = 0
if len(ordered_lines_list) == 0:
  ref_theme=""
else :
  ref_theme=ordered_lines_list[0].getTheme()
page_infos = []

for index in range(len(ordered_lines_list)) :
  if ordered_lines_list[index].getTheme()<>ref_theme :
    # enregistrement de la dernière page
    result.append(page_infos)
    # gestion de la nouvelle page
    nb_trous += on_page-compteur
    compteur = 0
    ref_theme = ordered_lines_list[index].getTheme()
    # gestion de la ligne
    page_infos = [ordered_lines_list[index].getTheme(), nb_trous, index]
    compteur += 1

  else :
    if compteur == on_page :
      # enregistrement de la dernière page
      result.append(page_infos)
      # gestion de la nouvelle page
      nb_trous += on_page-compteur
      compteur = 0
      ref_theme = ordered_lines_list[index].getTheme()
      # gestion de la ligne
      page_infos = [ordered_lines_list[index].getTheme(), nb_trous, index]
      compteur += 1
    else :
      # gestion de la ligne
      page_infos = [ordered_lines_list[index].getTheme(), nb_trous, index]
      compteur += 1

# ajout de la dernière page
result.append(page_infos)

return result
