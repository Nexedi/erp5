## Script (Python) "Invoice_zGetEscompteDescription"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
tmp_list = context.contentValues(filter={'portal_type':'Remise', 'discount_type_title':'Escompte'})

escompte_list = filter(lambda item: item.getDiscountType() == 'Escompte', tmp_list)

if escompte_list != []:
  escompte_object = escompte_list[0]
  if escompte_object.getDescription() != None: 
    escompte_description = string.replace(escompte_object.getDescription(),'%','%%')[:45]
  elif escompte_object.getDiscountRatio() != None:
    escompte_description = '%.2f' % (escompte_object.getDiscountRatio() * 100) + '%% sous 10 jours'
  else:
    escompte_description = '2%% sous 10 jours'
else:
  escompte_description = '2%% sous 10 jours'

return escompte_description
