parent_portal_type = context.getParent().getPortalType()
variation_dict = {}
for variation in context.getVariationText().split('\n') :
  variation_list = variation.split('/', 1)
  if len(variation_list) == 2 :
    variation_dict[variation_list[0]] = variation_list[1]
# fonctionne uniquement pour les cellule : dans le cas des lignes: les autres valaures sont ecrasé
dest_variation_dict = variation_dict.copy()
##########################################


# ceci est une transformation
# -> quand on fait une destruction de billet, une Destruction Line avec cash status to delete
# -> en source cash_status = to_delete; en destination cash_status = cancelled
# Faire la liste des modules qui demandent une transformation et coder la liste des modules en dur ici
#  avec les variations à forcer.

if 0 and parent_portal_type == 'Cash To Currency Purchase Line Out' :
  variation_dict['emission_letter'] = 'k'
  dest_variation_dict['cash_status'] = 'cancelled'

##########################################
variation_list = ['%s/%s' % (k, v) for k, v in variation_dict.items()]
dest_variation_list = ['%s/%s' % (k, v) for k, v in dest_variation_dict.items()]
variation_list.sort() ; dest_variation_list.sort()
return ['\n'.join(variation_list), '\n'.join(dest_variation_list)]
