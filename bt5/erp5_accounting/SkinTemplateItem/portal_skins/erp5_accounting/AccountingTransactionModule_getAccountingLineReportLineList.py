from Products.PythonScripts.standard import Object
line_list = []
request = context.REQUEST
portal = context.getPortalObject()
portal_selections = portal.portal_selections
selection_name = 'accounting_selection'
selection_params = portal_selections.getSelectionParamsFor(selection_name)

section_category = selection_params.get('section_category')
section_category_strict = selection_params.get('section_category_strict')


def isSource(accounting_transaction):
  if section_category:
    source_section = accounting_transaction.getSourceSectionValue()
    if source_section is None:
      return False
    group = source_section.getGroup(base=True)
    if section_category_strict:
      return group == section_category
    return (group or '').startswith(section_category)
  return accounting_transaction.AccountingTransaction_isSourceView()

def isDestination(accounting_transaction):
  if section_category:
    destination_section = accounting_transaction.getDestinationSectionValue()
    if destination_section is None:
      return False
    group = destination_section.getGroup(base=True)
    if section_category_strict:
      return group == section_category
    return (group or '').startswith(section_category)
  return accounting_transaction.AccountingTransaction_isDestinationView()


if section_category:
  currency = portal.Base_getCurrencyForSection(section_category)
  request.set('currency', currency)
  request.set('precision',
      portal.account_module.getQuantityPrecisionFromResource(currency))

checked_uid_list = \
    portal_selections.getSelectionCheckedUidsFor(selection_name)
if checked_uid_list:
  delivery_list = [brain.getObject() for brain in portal.portal_catalog(uid=checked_uid_list)]
else:
  params = portal_selections.getSelectionParamsFor(selection_name)
  params['limit'] = None # XXX potentially very big report
  delivery_list = portal_selections.callSelectionFor(
                                        selection_name,
                                        context=context,
                                        params=params)


account_reference_cache = {}
def getAccountReference(node):
  try:
    return account_reference_cache[node]
  except KeyError:
    if node is not None:
      reference = node.Account_getGapId()
    else:
      reference = ''
    account_reference_cache[node] = reference
    return reference

def getTitle(document):
  if document is not None:
    return document.getTranslatedTitle()
  return ''

bank_account_title_cache = {}
def getBankAccountTitle(bank_account):
  try:
    return bank_account_title_cache[bank_account]
  except KeyError:
    pass

  if bank_account is not None:
    reference = bank_account.getReference()
    title = bank_account.getTitle()
    if reference and reference != title:
      value = "%s - %s" % (reference, title)
    else:
      value = title
  else:
    value = ''
  bank_account_title_cache[bank_account] = value
  return value

accounting_currency_reference_cache = {}
def getAccountingCurrencyReference(section_relative_url):
  try:
    return accounting_currency_reference_cache[section_relative_url]
  except KeyError:
    reference = ''
    if section_relative_url:
      section = portal.restrictedTraverse(section_relative_url, None)
      if section is not None:
        reference = section.getProperty('price_currency_reference')
    accounting_currency_reference_cache[section_relative_url] = reference
    return reference


portal_type = context.getPortalAccountingMovementTypeList()

displayed_delivery_dict = {}
for delivery in delivery_list:
  if delivery.uid in displayed_delivery_dict: continue
  displayed_delivery_dict[delivery.uid] = True
  delivery = delivery.getObject()
  is_source = isSource(delivery)
  is_destination = isDestination(delivery)

  for movement in delivery.getMovementList(portal_type=portal_type):

    if is_source:
      node = movement.getSourceValue(portal_type='Account')
      node_title = ''
      node_account_type_title = ''
      node_financial_section_title = ''
      if node is not None:
        node_title = node.getTranslatedTitle()
        node_account_type_title = node.getAccountTypeTranslatedTitle()
        node_financial_section_title = \
          node.getFinancialSectionTranslatedTitle()

        line_list.append(Object(
        title=movement.hasTitle() and movement.getTitle() or
                     delivery.getTitle(),
        int_index=movement.getIntIndex(),
        string_index=movement.getStringIndex(),
        parent_description=delivery.getDescription(),
        parent_comment=delivery.getComment(),
        parent_reference=delivery.getReference(),
        specific_reference=delivery.getSourceReference(),
        node_reference=getAccountReference(node),
        node_title=node_title,
        node_account_type_title=node_account_type_title,
        node_financial_section_title=node_financial_section_title,
        section_title=movement.getSourceSectionTitle(),
        payment_title=getBankAccountTitle(movement.getSourcePaymentValue()),
        payment_mode=movement.getPaymentModeTranslatedTitle(),
        mirror_section_title=movement.getDestinationSectionTitle(),
        mirror_payment_title=getBankAccountTitle(movement.getDestinationPaymentValue()),
        mirror_section_region_title=movement.getDestinationSection() and
          movement.getDestinationSectionValue().getRegionTranslatedTitle(),
        function_title=getTitle(movement.getSourceFunctionValue()),
        function_reference=movement.getSourceFunctionReference(),
        project_title=getTitle(movement.getSourceProjectValue()),
        funding_title=getTitle(movement.getSourceFundingValue()),
        funding_reference=movement.getSourceFundingReference(),
        product_line=movement.getProductLineTranslatedTitle(),
        date=movement.getStartDate(),
        debit_price=movement.getSourceInventoriatedTotalAssetDebit(),
        credit_price=movement.getSourceInventoriatedTotalAssetCredit(),
        price=(movement.getSourceInventoriatedTotalAssetCredit() - movement.getSourceInventoriatedTotalAssetDebit()),
        currency=getAccountingCurrencyReference(movement.getSourceSection()),
        debit=movement.getSourceDebit(),
        credit=movement.getSourceCredit(),
        quantity=(movement.getSourceCredit() - movement.getSourceDebit()),
        resource=movement.getResourceReference(),
        quantity_precision=movement.getQuantityPrecisionFromResource(movement.getResource()),
        translated_portal_type=movement.getTranslatedPortalType(),
        parent_translated_portal_type=delivery.getTranslatedPortalType(),
        translated_simulation_state_title=movement.getTranslatedSimulationStateTitle(),))

    if is_destination:
      node = movement.getDestinationValue(portal_type='Account')
      node_title = ''
      node_account_type_title = ''
      node_financial_section_title = ''
      if node is not None:
        node_title = node.getTranslatedTitle()
        node_account_type_title = node.getAccountTypeTranslatedTitle()
        node_financial_section_title = \
          node.getFinancialSectionTranslatedTitle()

        line_list.append(Object(
        title=movement.hasTitle() and movement.getTitle() or
                     delivery.getTitle(),
        int_index=movement.getIntIndex(),
        string_index=movement.getStringIndex(),
        parent_description=delivery.getDescription(),
        parent_comment=delivery.getComment(),
        parent_reference=delivery.getReference(),
        specific_reference=delivery.getDestinationReference(),
        node_reference=getAccountReference(node),
        node_title=node_title,
        node_account_type_title=node_account_type_title,
        node_financial_section_title=node_financial_section_title,
        section_title=movement.getDestinationSectionTitle(),
        payment_title=getBankAccountTitle(movement.getDestinationPaymentValue()),
        payment_mode=movement.getPaymentModeTranslatedTitle(),
        mirror_section_title=movement.getSourceSectionTitle(),
        mirror_section_region_title=movement.getSourceSection() and
          movement.getSourceSectionValue().getRegionTranslatedTitle(),
        mirror_payment_title=getBankAccountTitle(movement.getSourcePaymentValue()),
        function_title=getTitle(movement.getDestinationFunctionValue()),
        function_reference=movement.getDestinationFunctionReference(),
        funding_title=getTitle(movement.getDestinationFundingValue()),
        funding_reference=movement.getDestinationFundingReference(),
        project_title=getTitle(movement.getDestinationProjectValue()),
        product_line=movement.getProductLineTranslatedTitle(),
        date=movement.getStopDate(),
        debit_price=movement.getDestinationInventoriatedTotalAssetDebit(),
        credit_price=movement.getDestinationInventoriatedTotalAssetCredit(),
        price=(movement.getDestinationInventoriatedTotalAssetCredit() - movement.getDestinationInventoriatedTotalAssetDebit()),
        currency=getAccountingCurrencyReference(movement.getDestinationSection()),
        debit=movement.getDestinationDebit(),
        credit=movement.getDestinationCredit(),
        quantity=(movement.getDestinationCredit() - movement.getDestinationDebit()),
        resource=movement.getResourceReference(),
        quantity_precision=movement.getQuantityPrecisionFromResource(movement.getResource()),
        translated_portal_type=movement.getTranslatedPortalType(),
        parent_translated_portal_type=delivery.getTranslatedPortalType(),
        translated_simulation_state_title=movement.getTranslatedSimulationStateTitle(),))


return line_list
