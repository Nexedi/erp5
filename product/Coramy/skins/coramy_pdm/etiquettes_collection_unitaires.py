## Script (Python) "etiquettes_collection_unitaires"
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
tab = '\t'
cr = '\r'
export = ''

for modele_item in modele_list:
  ligne_modele = ''
  modele=modele_item.getObject()

  ligne_modele += modele.getId()+tab
  ligne_modele += modele.getCollection()+tab
  ligne_modele += string.capwords(modele.getComposition())+tab
  ligne_modele += modele.getCodeEan13()+tab

  content_list = modele.objectValues()
  price_list = []
  for content_item in content_list:
    if content_item.portal_type == 'Element Tarif':
      price_list.append(content_item)

  for price in price_list:
    ligne_modele += price.description+tab
    ligne_modele += str(price.destination_base_price)+tab
  for i in range(3-len(price_list)):
    ligne_modele += tab+tab

  ligne_modele += cr
  export += ligne_modele

request.RESPONSE.setHeader('Content-Type','application/text')

return export
