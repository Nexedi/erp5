## Script (Python) "samples_to_produce"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
tab = '\t'
cr = '\r'
liste='Modele'+tab+'Qte livree'+tab+'Qte commandee'+cr
delivered_modele_list = context.samples_delivered()
ordered_modele_list = context.samples_ordered()
ordered_delivered_modele_list = context.samples_ordered_delivered()

delivered_modele_dict ={}
for modele in delivered_modele_list :
  delivered_modele_dict[modele.id] = modele.quantity

ordered_modele_dict ={}
for modele in ordered_modele_list :
  ordered_modele_dict[modele.id] = modele.quantity

for modele in ordered_delivered_modele_list :
  ordered_modele_dict[modele.id] = ordered_modele_dict[modele.id] - modele.quantity

delivered_modele_keys = delivered_modele_dict.keys()
ordered_modele_keys = ordered_modele_dict.keys()
for modele_key in ordered_modele_keys:
  if not(modele_key in delivered_modele_keys) :
    delivered_modele_dict[modele_key] = 0

delivered_modele_keys = delivered_modele_dict.keys()
delivered_modele_keys.sort()
for modele_key in delivered_modele_keys:
  if modele_key in ordered_modele_keys :
    liste += 'modele/'+modele_key+tab+str(int(delivered_modele_dict[modele_key]))+tab+str(int(ordered_modele_dict[modele_key]))+cr
  else :
    liste += 'modele/'+modele_key+tab+str(int(delivered_modele_dict[modele_key]))+tab+'0'+cr

request.RESPONSE.setHeader('Content-Type','application/text')

return liste
