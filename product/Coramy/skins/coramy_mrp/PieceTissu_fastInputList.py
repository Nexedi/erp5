## Script (Python) "PieceTissu_fastInputList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
text_list =  ['Quantité (m)_______________', 'Laize utile (cm)___________', 'N° fournisseur_____________', 'N° de bain de teinture_____', 'Commentaires______________']
property_list = ['quantity', 'laize_utile', 'source_reference', 'bain_teinture', 'comment']

fast_input_list =[text_list,property_list]

return fast_input_list
