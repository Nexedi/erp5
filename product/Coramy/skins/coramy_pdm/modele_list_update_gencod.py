## Script (Python) "modele_list_update_gencod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
selection = context.portal_selections.getSelectionFor('modele_selection',REQUEST=context.REQUEST)
modele_list = selection(context=context)
request = context.REQUEST
CIP = 650000

for modele_item in modele_list:
  modele=modele_item.getObject()
  modele.edit(code_ean13 = modele.new_ean13_code('3','15971',CIP))
  CIP += 1
