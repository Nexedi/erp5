from Products.PythonScripts.standard import Object
line_list = []
portal = context.getPortalObject()

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


for delivery in portal.portal_catalog(uid=uid_list or -1):
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
