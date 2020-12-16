from Products.PythonScripts.standard import Object
line_list = []
portal = context.getPortalObject()

# XXX use a larger limit
saved_selection_params = context.getPortalObject().portal_selections.getSelectionParamsFor(module_selection_name)
selection_params = saved_selection_params.copy()
selection_params['limit'] = 10000
context.getPortalObject().portal_selections.setSelectionParamsFor(module_selection_name, selection_params)

try:
  checked_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(module_selection_name)
  if checked_uid_list:
    getObject = portal.portal_catalog.getObject
    delivery_list = [getObject(uid) for uid in checked_uid_list]
  else:
    delivery_list = portal.portal_selections.callSelectionFor(module_selection_name, context=context)
finally:
  context.getPortalObject().portal_selections.setSelectionParamsFor(module_selection_name, saved_selection_params)

account_title_cache = {}
def getAccountTitle(relative_url):
  try:
    return account_title_cache[relative_url]
  except KeyError:
    if relative_url:
      title = \
        portal.restrictedTraverse(relative_url).Account_getFormattedTitle()
    else:
      title = ''
    account_title_cache[relative_url] = title
    return title


for delivery in delivery_list:
  delivery = delivery.getObject()
  for movement in delivery.getMovementList(portal_type=portal_type):
    line_list.append(Object(
        int_index=movement.getIntIndex(),
        title=movement.getTitle(),
        description=movement.getDescription(),
        reference=movement.getReference(),
        parent_title=delivery.getTitle(),
        parent_description=delivery.getDescription(),
        parent_reference=delivery.getReference(),
        parent_source_reference=delivery.getSourceReference(),
        parent_destination_reference=delivery.getDestinationReference(),
        source_title=movement.getSourceTitle(),
        destination_title=movement.getDestinationTitle(),
        source_section_title=movement.getSourceSectionTitle(),
        destination_section_title=movement.getDestinationSectionTitle(),
        source_administration_title=movement.getSourceAdministrationTitle(),
        destination_administration_title=movement.getDestinationAdministrationTitle(),
        source_trade_title=movement.getSourceTradeTitle(),
        destination_trade_title=movement.getDestinationTradeTitle(),
        source_function_title=movement.getSourceFunctionTitle(),
        destination_function_title=movement.getDestinationFunctionTitle(),
        source_decision_title=movement.getSourceDecisionTitle(),
        destination_decision_title=movement.getDestinationDecisionTitle(),
        source_account=getAccountTitle(movement.getSourceAccount()),
        destination_account=getAccountTitle(movement.getDestinationAccount()),
        start_date=movement.getStartDate(),
        stop_date=movement.getStopDate(),
        quantity=movement.getQuantity(),
        quantity_unit=movement.getQuantityUnitTitle(),
        resource_title=movement.getResourceTitle(),
        resource_reference=movement.getResourceReference(),
        product_line=movement.getProductLineTitle(),
        price=movement.getPrice(),
        total_price=movement.getTotalPrice(),
        price_currency=movement.getPriceCurrencyReference(),
        translated_portal_type=movement.getTranslatedPortalType(),
        parent_translated_portal_type=delivery.getTranslatedPortalType(),
        translated_simulation_state_title=movement.getTranslatedSimulationStateTitle()))

return line_list
