## Script (Python) "modele_list_export"
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

for modele_item in modele_list:
  modele=modele_item.getObject()
  if modele <> None :

    ligne_modele = ''
    ligne_modele += str(modele.getId())+'\t'
    ligne_modele += str(modele.getModeleOrigine())+'\t'
    ligne_modele += str(modele.getCollection())+'\t'

    print ligne_modele

request.RESPONSE.setHeader('Content-Type','application/text')

return printed
