## Script (Python) "purchase_order_apply_condition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
# appelé sur une commande, ce script recherche une condition d'achat
# pouvant s'appliquer à la commande et, s'il en trouve une (et une seule)
# complète le profil de la commande, le paiement, les remises

order = context
condition_list = []

# on commence par regarder si une condition d'achat est associée à la commande
condition_list = order.getSpecialiseValueList(portal_type=('Condition Achat',))
if len(condition_list) == 0 :

  # RECHERCHE d'une condition d'achat compatible
  # la recherche se fait d'abord sur le couple 'destination_section' et 'source'

  my_destination_section = order.getDestinationSectionValue()
  if my_destination_section <> None :
    my_destination_section_uid = my_destination_section.getUid()
  else :
    my_destination_section = ''
  my_source = order.getSourceValue()
  if my_source <> None :
    my_source_uid = my_source.getUid()
  else :
    my_source_uid = ''
  my_destination = order.getDestinationValue()
  if my_destination <> None :
    my_destination_uid = my_destination.getUid()
  else :
    my_destination_uid = ''
  condition_list = order.condition_achat_sql_search(destination_section_uid=my_destination_section_uid, source_uid=my_source_uid, destination_uid="")

  # s'il y a plus d'une condition trouvee, on essaye de réduire le choix
  # en intégrant un critère de recherche sur 'destination'
  if len(condition_list) > 1 :
    condition_list = order.condition_achat_sql_search(destination_section_uid=my_destination_section_uid, source_uid=my_source_uid, destination_uid=my_destination_uid)

# resultat des courses sur le recherche
if len(condition_list ) == 0 :
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=Pas+de+condition+achat+applicable.')
elif len(condition_list ) > 1 :
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=Trop+de+conditions+achat+applicables.')
else : # on a une condition applicable
  condition=condition_list[0].getObject()

  # MISE A JOUR DU PROFIL DE LA COMMANDE

  categories = order.getCategoryList()
  # DESTINATION
  if order.getDestinationValue() == None and condition.getDestinationValue() <> None :
    categories += ('destination/'+condition.getDestinationValue().getRelativeUrl(),)
  # destination_decision
  if order.getDestinationDecisionValue() == None and condition.getDestinationDecisionValue() <> None :
    categories += ('destination_decision/'+condition.getDestinationDecisionValue().getRelativeUrl(),)
  # destination_administration
  if order.getDestinationAdministrationValue() == None and condition.getDestinationAdministrationValue() <> None :
    for destination_administration_item in condition.getDestinationAdministrationValueList() :
      categories += ('destination_administration/'+destination_administration_item.getRelativeUrl(),)
  # destination_payment
  if order.getDestinationPaymentValue() == None and condition.getDestinationPaymentValue() <> None :
    categories += ('destination_payment/'+condition.getDestinationPaymentValue().getRelativeUrl(),)

  # SOURCE_section
  if order.getSourceSectionValue() == None :
    if condition.getSourceSectionValue() <> None :
      categories += ('source_section/'+condition.getSourceSectionValue().getRelativeUrl(),)
    # si source_section pas presente dans la condition achat, on utilise source de order
    else :
      categories += ('source_section/'+order.getSourceValue().getRelativeUrl(),)
  # source_decision
  if order.getSourceDecisionValue() == None :
    if condition.getSourceDecisionValue() <> None :
      categories += ('source_decision/'+condition.getSourceDecisionValue().getRelativeUrl(),)
    # si source_decision pas presente dans la condition achat, on utilise source de order
    else :
      categories += ('source_decision/'+order.getSourceValue().getRelativeUrl(),)
  # source_administration
  if order.getSourceAdministrationValue() == None :
    if condition.getSourceAdministrationValue() <> None :
      categories += ('source_administration/'+condition.getSourceAdministrationValue().getRelativeUrl(),)
    # si source_administration pas presente dans la condition achat, on utilise source de order
    else :
      categories += ('source_administration/'+order.getSourceValue().getRelativeUrl(),)
  # source_payment
  if order.getSourcePaymentValue() == None :
    if condition.getSourcePaymentValue() <> None :
      categories += ('source_payment/'+condition.getSourcePaymentValue().getRelativeUrl(),)
    # si source_payment pas presente dans la condition achat, on utilise source de order
    else :
      categories += ('source_payment/'+order.getSourceValue().getRelativeUrl(),)

  # MISE A JOUR DU PAIEMENT DE LA COMMANDE
  my_payment_term=''
  if order.hasPaymentTerm() :
    my_payment_term = order.getPaymentTerm()
  elif condition.hasPaymentTerm() :
    my_payment_term = condition.getPaymentTerm()

  my_payment_end_of_month=''
  if order.hasPaymentEndOfMonth() :
    my_payment_end_of_month = order.getPaymentEndOfMonth()
  elif condition.hasPaymentTerm() :
    my_payment_end_of_month = condition.getPaymentEndOfMonth()

  my_payment_additional_term=''
  if order.hasPaymentAdditionalTerm() :
    my_payment_additional_term = order.getPaymentAdditionalTerm()
  elif condition.hasPaymentAdditionalTerm() :
    my_payment_additional_term = condition.getPaymentAdditionalTerm()

  if order.getPaymentModeValue() == None and condition.getPaymentModeValue() <> None :
    categories += (condition.getPaymentModeValue().getRelativeUrl(),)
  if order.getTradeDateValue() == None and condition.getTradeDateValue() <> None :
    categories += (condition.getTradeDateValue().getRelativeUrl(),)

  # copie des conditions de paiement additionnelles si pas presentes dans commande
  if len(order.contentIds(filter={'portal_type':'Condition Paiement'})) == 0 :
    to_copy=[]
    to_copy=condition.contentIds(filter={'portal_type':'Condition Paiement'})
    if len(to_copy)>0 :
     copy_data = condition.manage_copyObjects(ids=to_copy)
     new_id_list = order.manage_pasteObjects(copy_data)

  # copie des remises si pas presentes dans commande
  if len(order.contentIds(filter={'portal_type':'Remise'})) == 0 :
    to_copy=[]
    to_copy=condition.contentIds(filter={'portal_type':'Remise'})
    if len(to_copy)>0 :
     copy_data = condition.manage_copyObjects(ids=to_copy)
     new_id_list = order.manage_pasteObjects(copy_data)

  # copie des conditions logistique
  if order.getIncotermValue() == None and condition.getIncotermValue() <> None :
    categories += (condition.getIncotermValue().getRelativeUrl(),)
  if order.getDeliveryModeValue() == None and condition.getDeliveryModeValue() <> None :
    categories += (condition.getDeliveryModeValue().getRelativeUrl(),)

  # copie de la devise
  if order.getPriceCurrencyValue() == None and condition.getPriceCurrencyValue() <> None :
    categories += ('price_currency/'+condition.getPriceCurrencyValue().getRelativeUrl(),)

  # copie du code client
  my_destination_decision_source_reference = ''
  if order.hasDestinationDecisionSourceReference() :
    my_destination_decision_source_reference = order.getDestinationDecisionSourceReference()
  elif condition.hasDestinationDecisionSourceReference() :
    my_destination_decision_source_reference = condition.getDestinationDecisionSourceReference()

  # mise à jour du lien specialise entre order et condition appliquee
  final_categories = ()
  for category_item in categories :
    if category_item.find('specialise/') == (-1):
      final_categories += (category_item,)

  final_categories += ('specialise/'+condition.getRelativeUrl(),)

  order.edit(categories=final_categories, payment_term=my_payment_term,
             payment_end_of_month=my_payment_end_of_month,
             payment_additional_term=my_payment_additional_term,
             destination_decision_source_reference = my_destination_decision_source_reference)

  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=Commande+mise+a+jour.')

return redirect_url
