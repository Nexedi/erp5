## Script (Python) "sales_order_apply_condition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,batch_mode=0
##title=
##
# appelé sur une commande, ce script recherche une condition de vente
# pouvant s'appliquer à la commande et, s'il en trouve une (et une seule)
# complète le profil de la commande, le paiment, les remises

order = context
condition_list = []

# on commence par regarder si une condition de vente est associée à la commande
condition_list = order.getSpecialiseValueList(portal_type=('Condition Vente',))
if len(condition_list) == 0 :

  # RECHERCHE d'une condition de vente compatible
  # la recherche se fait d'abord sur le couple 'source_section' et 'destination'

  my_source_section = order.getSourceSectionValue()
  if my_source_section <> None :
    my_source_section_uid = my_source_section.getUid()
  else :
    my_source_section_uid = ''
  my_destination = order.getDestinationValue()
  if my_destination <> None :
    my_destination_uid = my_destination.getUid()
  else :
    my_destination_uid = ''
  my_group = order.getGroupValue()
  if my_group <> None :
    my_group_uid = my_group.getUid()
  else :
    my_group_uid = ''
  my_destination_decision = order.getDestinationDecisionValueList(portal_type=('Organisation','Category'))
  if len(my_destination_decision) > 0 :
    my_destination_decision_uid = my_destination_decision[0].getUid()
  else :
    my_destination_decision_uid = ''
  condition_list = order.condition_vente_sql_search(source_section_uid=my_source_section_uid, destination_uid=my_destination_uid, group_uid="", destination_decision_uid="")

  # si on a trouve une ou plusieurs conditions de vente on s'arrete
  # sinon on refait une recherche sur le couple 'source-section' et 'group'
  if len(condition_list ) == 0 :
    condition_list = order.condition_vente_sql_search(source_section_uid=my_source_section_uid, destination_uid="", group_uid=my_group_uid, destination_decision_uid="")
    if len(condition_list) > 1 :
      # s'il y a plus d'une condition trouvee, on essaye de réduire le choix
      # en intégrant un critère de recherche sur 'destination_decision'
      condition_list = order.condition_vente_sql_search(source_section_uid=my_source_section_uid, destination_uid="", group_uid=my_group_uid, destination_decision_uid=my_destination_decision_uid)

  # s'il y a plus d'une condition trouvee, on essaye de réduire le choix
  # en intégrant un critère de recherche sur 'destination_decision'
  elif len(condition_list) > 1 :
    condition_list = order.condition_vente_sql_search(source_section_uid=my_source_section_uid, destination_uid=my_destination_uid, group_uid="", destination_decision_uid=my_destination_decision)

# resultat des courses sur le recherche
if len(condition_list ) == 0 :
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=Pas+de+condition+de+vente+applicable.')
elif len(condition_list ) > 1 :
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=Trop+de+conditions+de+vente+applicables.')
else : # on a une condition applicable
  condition=condition_list[0].getObject()

  # MISE A JOUR DU PROFIL DE LA COMMANDE

  categories = order.getCategoryList()
  # SOURCE
  if order.getSourceValue() == None and condition.getSourceValue() <> None :
    categories += ('source/'+condition.getSourceValue().getRelativeUrl(),)
  # source_decision
  if order.getSourceDecisionValue() == None and condition.getSourceDecisionValue() <> None :
    categories += ('source_decision/'+condition.getSourceDecisionValue().getRelativeUrl(),)
  # source_administration
  if order.getSourceAdministrationValue() == None and condition.getSourceAdministrationValue() <> None :
    categories += ('source_administration/'+condition.getSourceAdministrationValue().getRelativeUrl(),)
  # source_payment
  if order.getSourcePaymentValue() == None and condition.getSourcePaymentValue() <> None :
    categories += ('source_payment/'+condition.getSourcePaymentValue().getRelativeUrl(),)

  # DESTINATION_section
  if order.getDestinationSectionValue() == None :
    if condition.getDestinationSectionValue() <> None :
      categories += ('destination_section/'+condition.getDestinationSectionValue().getRelativeUrl(),)
    # si destination_section pas presente dans la condition de vente, on utilise destination de order
    else :
      categories += ('destination_section/'+order.getDestinationValue().getRelativeUrl(),)
  # destination_decision
  if order.getDestinationDecisionValue(portal_type='Organisation') == None :
    if condition.getDestinationDecisionValue(portal_type='Organisation') <> None :
      categories += ('destination_decision/'+condition.getDestinationDecisionValue(portal_type='Organisation').getRelativeUrl(),)
    # si destination_decision pas presente dans la condition de vente, on utilise destination de order
    else :
      categories += ('destination_decision/'+order.getDestinationValue().getRelativeUrl(),)
  # destination_administration
  if order.getDestinationAdministrationValue() == None :
    if condition.getDestinationAdministrationValue() <> None :
      categories += ('destination_administration/'+condition.getDestinationAdministrationValue().getRelativeUrl(),)
    # si destination_administration pas presente dans la condition de vente, on utilise destination de order
    else :
      categories += ('destination_administration/'+order.getDestinationValue().getRelativeUrl(),)
  # destination_payment
  if order.getDestinationPaymentValue() == None :
    if condition.getDestinationPaymentValue() <> None :
      categories += ('destination_payment/'+condition.getDestinationPaymentValue().getRelativeUrl(),)
    # si destination_payment pas presente dans la condition de vente, on utilise destination de order
    else :
      categories += ('destination_payment/'+order.getDestinationValue().getRelativeUrl(),)

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

  # copie du code fournisseur
  my_source_decision_destination_reference = ''
  if order.hasSourceDecisionDestinationReference() :
    my_source_decision_destination_reference = order.getSourceDecisionDestinationReference()
  elif condition.hasSourceDecisionDestinationReference() :
    my_source_decision_destination_reference = condition.getSourceDecisionDestinationReference()

  # mise à jour du lien specialise entre order et condition appliquee
  final_categories = ()
  for category_item in categories :
    if category_item.find('specialise/') == (-1):
      final_categories += (category_item,)

  final_categories += ('specialise/'+condition.getRelativeUrl(),)

  order.edit(categories=final_categories, payment_term=my_payment_term,
             payment_end_of_month=my_payment_end_of_month,
             payment_additional_term=my_payment_additional_term,
             source_decision_destination_reference = my_source_decision_destination_reference)

  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=Commande+mise+a+jour.')

if batch_mode:
  return None
else:
  context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
