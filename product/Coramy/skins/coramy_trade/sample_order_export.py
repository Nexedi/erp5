## Script (Python) "sample_order_export"
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
tab = '\t'
cr = '\r'
ligne_modele = ''

for ligne in lignes_list:
  modele=ligne.getDefaultValue('resource',portal_type=['Modele'])

  ligne_modele += modele.getId()+tab
  ligne_modele += modele.getCollection()+tab
  ligne_modele += string.capwords(string.lower(modele.getComposition('')))+tab
  ligne_modele += modele.getCodeEan13()+tab
  ligne_modele += string.lower(modele.getDescription('')[0:20])+tab

  price_list = ligne.contentValues(filter={'portal_type':'Element Tarif'})

  for price in price_list:
    printed_price=0
    ligne_modele += string.lower(price.getDescription(''))+tab
    for qty in possible_qty:
      qty_price = price.getCell(None, qty, base_id='destination_base_price')
      if qty_price <>None:
        printed_price +=1
        ligne_modele += str(int(qty))+tab
        ligne_modele += str(qty_price.getProperty(key='destination_base_price'))+tab
    for i in range(3-printed_price):
      ligne_modele += tab+tab

  ligne_modele += cr

request.RESPONSE.setHeader('Content-Type','application/text')

return ligne_modele
