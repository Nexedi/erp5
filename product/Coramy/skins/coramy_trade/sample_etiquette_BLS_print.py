## Script (Python) "sample_etiquette_BLS_print"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
sample_order=context
lignes_list = sample_order.contentValues(filter={'portal_type':'Sample Order Line'})
request = context.REQUEST
possible_qty=('00300','01000','05000','10000')

for ligne in lignes_list:
  modele=ligne.getDefaultValue('resource',portal_type=['Modele'])

  if modele <> None :
    ligne_modele = ''
    ligne_modele += modele.getDestinationReference()+'£'
    ligne_modele += modele.getCollection()+'£'
    ligne_modele += string.capwords(string.lower(modele.composition))+'£'

    price_list = ligne.contentValues(filter={'portal_type':'Element Tarif'})

    for price in price_list:
      printed_price=0
      ligne_modele += string.lower(price.description)+'£'
      for qty in possible_qty:
        qty_price = price.getCell(None, qty, base_id='destination_base_price')
        if qty_price <>None:
          printed_price +=1
          ligne_modele += str(int(qty))+'£'
          ligne_modele += str(qty_price.getProperty(key='destination_base_price'))+'£'
      for i in range(4-printed_price):
        ligne_modele += '££'

    print ligne_modele

request.RESPONSE.setHeader('Content-Type','application/text')

return printed
