# listbox is not passed at the first time when this script is called.
# when the user clicks on the Update button, listbox is passed, and
# the contents must be preserved in the form.
#
# rendering_vault : the vault that we want to render, if specified we will use
#                   getInventory in order to automatically full the fast input

from Products.ERP5Type.Cache import CachingMethod
portal = context.getPortalObject()
precision = 0
if listbox is None:
  # This is the first time.
  cash_status_list          = cash_detail_dict['cash_status_list']
  emission_letter_list      = cash_detail_dict['emission_letter_list']
  variation_list            = cash_detail_dict['variation_list']
  operation_currency        = cash_detail_dict['operation_currency']
  line_portal_type          = cash_detail_dict['line_portal_type']
  column_base_category      = cash_detail_dict['column_base_category']
  read_only                 = cash_detail_dict['read_only']
  check_float               = int(cash_detail_dict.get('check_float', 1))
  currency_cash_portal_type = cash_detail_dict['currency_cash_portal_type']

  if fast_input_title is None:
    # Module getTranslatedTitle does not return a translated string.
    # Borrow code from ERP5Site_getModuleItemList to achieve hand translation.
    # XXX: Pass title value as a list to work around an encoding bug in TextWidget:
    #  It renders given value as a list of str, and casting to str throws an error when
    #  encountering UTF-8 chars. This cast is not called when provided value is a tuple
    # or a list...
    fast_input_title = ['%s - %s' % \
      (context.getPortalObject().Localizer.erp5_ui.gettext(context.getParentValue().getTitle()),
       context.getSourceReference())]
  if 'target_total_price' not in kw:
    target_total_price = context.getSourceTotalAssetPrice()
  else:
    target_total_price = kw.pop('target_total_price')

  # If use_inventory is passed, use that value. Otherwise, assume False.
  # use_inventory = cash_detail_dict.get('use_inventory', False)
  # assume this is always false as we don't need to distinguish this anymore
  use_inventory = False

  if currency_cash_portal_type is None:
    currency_cash_portal_type = ('Banknote','Coin')

  # If not passed, get the category IDs from the database.
  if cash_status_list is None:
    cash_status_list = list(context.portal_categories.cash_status.objectIds())
  if emission_letter_list is None :
    emission_letter_list = list(context.portal_categories.emission_letter.objectIds())
  if variation_list is None :
    variation_list = list(context.portal_categories.variation.objectIds())

  def generic_prioritized_sort(a, b, priority_list):
    if a == b:
      return 0
    a_in_list = a in priority_list
    b_in_list = b in priority_list
    if a_in_list and (not b_in_list):
      return -1
    elif (not a_in_list) and b_in_list:
      return 1
    elif (not b_in_list) or (a > b):
      return -1
    elif (not a_in_list) or (a < b):
      return 1

  prioritized_banknote_emission_letter_list = context.Baobab_getUserEmissionLetterList()
  prioritized_coin_cash_status_list = prioritized_coin_emission_letter_list = ['not_defined']

  def banknote_emission_letter_sort(a, b):
    return generic_prioritized_sort(a, b, prioritized_banknote_emission_letter_list)

  def coin_emission_letter_sort(a, b):
    return  generic_prioritized_sort(a, b, prioritized_coin_emission_letter_list)

  def coin_cash_status_sort(a, b):
    return  generic_prioritized_sort(a, b, prioritized_coin_cash_status_list)

  # Make sure to use separate instances of the lists.
  banknote_cash_status_list = cash_status_list
  coin_cash_status_list = [x for x in cash_status_list]
  banknote_emission_letter_list = emission_letter_list
  coin_emission_letter_list = [x for x in emission_letter_list]

  # Sort the lists for consistency.
  banknote_cash_status_list.sort()
  banknote_emission_letter_list.sort(banknote_emission_letter_sort)
  coin_cash_status_list.sort(coin_cash_status_sort)
  coin_emission_letter_list.sort(coin_emission_letter_sort)
  variation_list.sort()

  # Get the currency cash objects for a given currency.
  currency = 'currency_module/%s' % operation_currency
  # This is very bad to call catalog each time, it is the bottleneck,
  # So we will add a caching method here
  def getCurrencyCashRelativeUrlList(currency=None, currency_cash_portal_type=None):
    result = context.portal_catalog(portal_type = currency_cash_portal_type)
    currency_cash_list = [x.getObject() for x in result 
                          if x.getObject().getPriceCurrency() == currency 
                          and len(x.getObject().getVariationList())>0]
    return [x.getRelativeUrl() for x in currency_cash_list]
  getCurrencyCashRelativeUrlList = CachingMethod(getCurrencyCashRelativeUrlList, 
                               id=('CashDelivery_generateCashDetailInputDialog', 
                                              'getCurrencyCashRelativeUrlList'), 
                               cache_factory='erp5_ui_long')
  currency_cash_url_list = getCurrencyCashRelativeUrlList(currency=currency,
                              currency_cash_portal_type=currency_cash_portal_type)
  currency_cash_list = [portal.restrictedTraverse(x) for x in currency_cash_url_list]

  # This is the same thing, but by using catalog, so this is not nice at all
  #result = context.portal_catalog(portal_type = currency_cash_portal_type)
  #currency_cash_list = [x.getObject() for x in result if x.getObject().getPriceCurrency() == currency and len(x.getObject().getVariationList())>0]


  # If only one variation is specified, we want to display a part of cash currencies which
  # exists in this variation (creation year, such as 2003).
  if len(variation_list) == 1:
    new_currency_cash_list = []
    variation = variation_list[0]
    for currency_cash in currency_cash_list:
      if variation in currency_cash.getVariationList():
        new_currency_cash_list.append(currency_cash)
    currency_cash_list = new_currency_cash_list

  currency_cash_list = context.Base_sortCurrencyCashList(currency_cash_list)

  # Get the axis information based on the specified column base category.
  # axis_list_dict contains the lists of objects, while axis_dict contains
  # the base categories.
  if column_base_category == 'cash_status':
    axis_list_dict = {
                        'column': cash_status_list,
                        'line1' : emission_letter_list,
                        'line2' : variation_list
                     }
    axis_dict      = {
                        'column': 'cash_status',
                        'line1': 'emission_letter',
                        'line2': 'variation'
                     }
  elif column_base_category == 'emission_letter':
    axis_list_dict = {
                        'column': emission_letter_list,
                        'line1' : cash_status_list,
                        'line2' : variation_list
                     }
    axis_dict      = {
                        'column': 'emission_letter',
                        'line1': 'cash_status',
                        'line2': 'variation'
                     }
  else:
    # column_base_category == variation
    axis_list_dict = {
                        'column': variation_list,
                        'line1' : emission_letter_list,
                        'line2' : cash_status_list
                     }
    axis_dict      = {
                        'column': 'variation',
                        'line1': 'emission_letter',
                        'line2': 'cash_status'
                     }

  total_price = 0
  listbox = []

  inventory_dict = {}
  if rendering_vault is not None and len(context.objectValues(portal_type=line_portal_type))==0:
    # build the list of ressources for this vault
    inventory_list = context.CounterModule_getVaultTransactionList(vault=rendering_vault, at_date=context.getStartDate())
    # build the dict of ressources for this vault, the dict
    # allow to parse the list only one time
    for inventory in inventory_list:
      resource_id = inventory.resource_id
      resource_list = inventory_dict.setdefault(resource_id, [])
      resource_list.append(inventory)

  for currency_cash in currency_cash_list:
    if currency_cash.getPortalType() == 'Coin':
      cash_status_list = coin_cash_status_list
      emission_letter_list = coin_emission_letter_list
    else:
      cash_status_list = banknote_cash_status_list
      emission_letter_list = banknote_emission_letter_list
    # Search if the current object contains a line with a given portal type.
    currency_cash_id = currency_cash.getId()
    cash_delivery_line = context.CashDelivery_searchLineByResource(currency_cash_id, line_portal_type)
    # This variable counts the number of lines added for this currency cash.
    line_number = 0

    if cash_delivery_line is not None or len(inventory_dict.get(currency_cash_id, ()))>0:
      # If a line exists for this cash currency, add lines into the listbox according to
      # the currency information.
      #context.log("cash_delivery_line", "cash_delivery_line = %s, currency = %s, type = %s" %(cash_delivery_line, currency_cash, line_portal_type))
      currency_dict = None
      resource_price = currency_cash.getBasePrice()

      # Collect cells according to the categories.
      cell_dict_dict = {}
      cell_list = []
      if cash_delivery_line is not None:
        cell_list = cash_delivery_line.getCellValueList()
      else:
        # the result is inside the currency_dict
        cell_list = inventory_dict[currency_cash_id]
      for cell in cell_list:
        category1 = cell.getProperty(axis_dict['line1']).split('/')[-1]
        category2 = cell.getProperty(axis_dict['line2']).split('/')[-1]
        column_category = cell.getProperty(axis_dict['column']).split('/')[-1]
        key = (category1, category2)
        #context.log(str((key, axis_dict['column'], column_category, cell.getVariation())), cell)
        cell_dict_dict.setdefault(key, {})[column_category] = cell



      # Sort the keys to obtain a consistent behavior.
      key_list = cell_dict_dict.keys()
      key_list.sort(lambda a, b: cmp(a[0], b[0]) or cmp(a[1], b[1]))

      # Look at all the cells of the dictionary to add lines.
      for key in key_list:
        cell_dict = cell_dict_dict[key]
        total_quantity = 0
        currency_dict = None
        for counter, column in enumerate(axis_list_dict['column']):
          cell = cell_dict.get(column, None)
          #context.log("Cashdelivery_...", "cell = %s, column = %s"%(cell, column))
          if cell is None:
            continue

          # Get the quantity of the cell, and skip it if not significant.
          if use_inventory:
            quantity = cell.getInventory()
          else:
            quantity = cell.getProperty('quantity')
          if not quantity:
            continue

          if currency_dict is None:
            currency_dict = {
              'resource_translated_title': currency_cash.getTranslatedTitle(),
              'resource_id':               currency_cash.getId(),
              axis_dict['line1']:          key[0],
              axis_dict['line2']:          key[1],
            }

          currency_dict['column%d' % (counter + 1)] = quantity
          total_quantity += quantity
        #context.log("currency_dict", currency_dict)
        if currency_dict is not None:
          price = total_quantity * resource_price
          currency_dict['price'] = price
          total_price += price
          line_number += 1
          # set default value for column
          for counter, column in enumerate(axis_list_dict['column']):
            col_key = 'column%d' % (counter + 1)
            if not currency_dict.has_key(col_key):
              currency_dict[col_key] = 0
          currency_dict['number_line_to_add'] = 0
          listbox.append(currency_dict)

    if line_number == 0:
      # Add an empty line only if no line is present for this cash currency.
      currency_dict = {
        'resource_translated_title': currency_cash.getTranslatedTitle(),
        'resource_id': currency_cash.getId(),
        'emission_letter': emission_letter_list[0],
        'cash_status': cash_status_list[0],
        'variation': variation_list[0],
        'additional_line_number': 0,
        'price': 0,
        'number_line_to_add': 0
      }
      # set default value for column
      for counter, column in enumerate(axis_list_dict['column']):
        currency_dict['column%d' % (counter + 1)] = 0
      listbox.append(currency_dict)
      
  if check_float == 0:
    precision = 4
  other_parameter_list = (operation_currency, line_portal_type, read_only, column_base_category, use_inventory, fast_input_title[0], target_total_price, check_float)
  context.Base_updateDialogForm(listbox=listbox
                                , calculated_price=total_price
                                , empty_line_number=0
                                , cash_status_list = cash_status_list
                                , emission_letter_list = emission_letter_list
                                , variation_list = variation_list
                                , other_parameter = other_parameter_list
                                , fast_input_title=fast_input_title
                                , target_total_price=target_total_price
                                , precision=precision
                                , )

  return context.asContext(  context=None
                             , portal_type=context.getPortalType()
                             , calculated_price=total_price
                             , cash_status_list = cash_status_list
                             , emission_letter_list = emission_letter_list
                             , variation_list = variation_list
                             , other_parameter = other_parameter_list
                             , fast_input_title=fast_input_title
                             , target_total_price=target_total_price
                             , precision=precision
                             ).CashDetail_viewLineFastInputForm(**kw)


else :

  # we want to update the listbox
  cash_status_list          = kw['cash_status_list']
  emission_letter_list      = kw['emission_letter_list']
  variation_list            = kw['variation_list']
  other_parameter           = kw['other_parameter']
  operation_currency        = other_parameter[0]
  line_portal_type          = other_parameter[1]
  read_only                 = other_parameter[2]
  column_base_category      = other_parameter[3]
  use_inventory             = other_parameter[4]
  fast_input_title          = other_parameter[5]
  target_total_price        = other_parameter[6]
  check_float               = int(other_parameter[7])

  # we don't update anything in read only mode
  if read_only == "True":
    context.Base_updateDialogForm(listbox=listbox, empty_line_number=0)
    return context.asContext(context=None, portal_type=context.getPortalType() ,**kw ).CashDetail_viewLineFastInputForm(**kw)

  # get the maximum number of line allowed for a variation
  if column_base_category == 'cash_status':
    columne_base_list = cash_status_list
    max_lines =len(emission_letter_list) * len(variation_list)
  elif column_base_category == 'emission_letter':
    column_base_list = emission_letter_list
    max_lines =len(cash_status_list) * len(variation_list)
  else:
    column_base_list = variation_list
    max_lines =len(cash_status_list) * len(emission_letter_list)

  line_counter_dict = {}
  # compute number of exisiting lines for a resource
  for line in listbox:
    resource_key = line['resource_id']
    if line_counter_dict.has_key(resource_key):
      line_counter_dict[resource_key] = line_counter_dict[resource_key] + 1
    else:
      line_counter_dict[resource_key] = 1

  total_price = 0
  new_line_list = []
  next_listbox_key = max([int(x.get('listbox_key', 0)) for x in listbox]) + 1
  # browse line to determine new lines to add
  for line in listbox:
    # must get the resource
    resource_id = line['resource_id']
    # This is a huge performance problem to call many times the catalog
    # for each fast input !!!!
    #resource_list = context.portal_catalog(portal_type = ('Banknote','Coin') ,id = resource_id)
    #resource_price = resource_list[0].getObject().getBasePrice()
    resource_value = context.currency_cash_module[resource_id]
    resource_price = resource_value.getObject().getBasePrice()
    line['resource_translated_title'] = resource_value.getTranslatedTitle()
    # get the number of lines to add
    if line.has_key('number_line_to_add'):
      lines_to_add = int(line['number_line_to_add'])
    else:
      lines_to_add = 0
    line['number_line_to_add'] = 0
    # remove the key
    #del line['listbox_key']
    # create new line
    for num in xrange(lines_to_add):
      # make sure we don't have too many lines
      if line_counter_dict[resource_id] <= max_lines:
        line_counter_dict[resource_id] = line_counter_dict[resource_id] + 1
        new_line = line.copy()
        new_line['listbox_key'] = next_listbox_key
        next_listbox_key += 1
        # set default quantity to 0
        for column_nb in xrange(1, len(column_base_list) + 1):
          new_line['column%s' %(str(column_nb))] = 0
        new_line['price'] = 0
        new_line_list.append(new_line)
    # compute the price for existing line
    quantity = 0
    for column_nb in xrange(1, len(column_base_list) + 1):
      if line['column%s' %(str(column_nb))] != '' and line['column%s' %(str(column_nb))] is not None:
        quantity += line['column%s' %(str(column_nb))]
    line['price'] = resource_price * quantity
    total_price += line['price']
    # add current line
    new_line_list.append(line)

  if check_float == 0:
   precision = 4
  listbox = new_line_list
  context.Base_updateDialogForm(  listbox=listbox
                                  , calculated_price=total_price
                                  , empty_line_number=0
                                  , fast_input_title=fast_input_title
                                  , precision=precision
                                  , target_total_price=target_total_price)

  return context.asContext(  context=None
                             , portal_type=context.getPortalType()
                             , calculated_price=total_price
                             , fast_input_title=fast_input_title
                             , target_total_price=target_total_price
                             , precision=precision
                             ,**kw
                             ).CashDetail_viewLineFastInputForm(**kw)
