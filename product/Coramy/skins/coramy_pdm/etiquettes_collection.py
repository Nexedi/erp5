## Script (Python) "etiquettes_collection"
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

  ligne_modele = ''
  ligne_modele += modele.id+'£'
  ligne_modele += modele.getCollection()+'£'
  ligne_modele += modele.composition+'£'

  content_list = modele.objectValues()
  price_list = []
  for content_item in content_list:
    if content_item.portal_type == 'Element Tarif':
      price_list.append(content_item)

  for price in price_list:
    ligne_modele += price.description+'£'
    ligne_modele += str(price.destination_base_price)+'£'

#  ligne_modele += '$'
  print ligne_modele

request.RESPONSE.setHeader('Content-Type','application/text')

return printed
