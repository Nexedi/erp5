# Verbose is used when we do not want to use the user interface in order
# to have a nice error message
from Products.ERP5Type.Message import Message
from Products.ERP5Type.Document import newTempBase

request = context.REQUEST
item_model = context.getPortalObject().restrictedTraverse(resource)

# We must make sure that the selection is not None
# or the validator of the Listbox will not work
from Products.ERP5Form.Selection import Selection
selection = context.portal_selections.getSelectionFor('Check_fastInputForm_selection')
if selection is None:
  selection = Selection()
  context.portal_selections.setSelectionFor('Check_fastInputForm_selection',selection)

global error_value
error_value = 0
global field_error_dict
field_error_dict = {}

def generate_error(listbox_line, column_title, error_message):
  global error_value
  global field_error_dict
  # Generate an error which is displayed by the listbox
  error_id = 'listbox_%s_new_%s' % (column_title,\
                                    listbox_line['listbox_key'])
  error = newTempBase(context, error_id)
  error.edit(error_text=error_message)
  field_error_dict[error_id] = error
  error_value = 1

def convertTravelerCheckReferenceToInt(traveler_check_reference):
  """
    Convert a reaveler check reference into an int.
    Raise ValueError if traveler_check_reference doesn't have a valid format.
  """
  if not same_type(traveler_check_reference, ''):
    raise ValueError
  if len(traveler_check_reference) != 10:
    raise ValueError
  return int(traveler_check_reference[4:])

def convertCheckReferenceToInt(check_reference):
  if len(check_reference) != 7:
    raise ValueError('Check reference must be 7-char long.')
  return int(check_reference)

# listbox is not passed at the first time when this script is called.
# when the user clicks on the Update button, listbox is passed, and
# the contents must be preserved in the form.
if listbox in (None,()) or (previous_resource not in('',None) and previous_resource!=resource):
  listbox = []
else:
  for line in listbox:
    destination_payment_reference = line.get('destination_payment_reference',None)
    reference_range_min = line.get('reference_range_min',None)
    reference_range_max = line.get('reference_range_max',None)
    check_amount = line.get('check_amount',None)
    quantity = int(line.get('quantity',0))
    if quantity not in (None, 0) and item_model.isAccountNumberEnabled() \
        and destination_payment_reference in (None,''):
      message = 'You must define an account'
      generate_error(line,'destination_payment_reference',message)
    if destination_payment_reference not in (None,''):
      # String index contains the internal bank account reference
      account_list = [x.getObject() for x in
                      context.portal_catalog(portal_type='Bank Account',
                      string_index=destination_payment_reference)]
      if len(account_list)==0:
        message = 'This account number does not exist'
        if verbose:
          message = Message(domain='ui',message='$reference account number does not exist',
                            mapping={'reference':destination_payment_reference})
        generate_error(line,'destination_payment_reference',message)
      elif len(account_list)>1:
        message = 'This account number exist several times'
        if verbose:
          message = Message(domain='ui',message='$reference account number exist several times',
                            mapping={'reference':destination_payment_reference})
        generate_error(line,'destination_payment_reference',message)
      else:
        account = account_list[0]
        line['destination_payment_relative_url'] = account.getRelativeUrl()
        destination_trade = account.getParentValue()
        line['destination_trade_relative_url'] = destination_trade.getRelativeUrl()
      if reference_range_min in (None,''):
        message = 'Please set a start number'
        generate_error(line,'reference_range_min',message)
    if reference_range_max in (None,'') and reference_range_min not in (None,''):
      if quantity!=1:
        message = 'Please set a stop number'
        generate_error(line,'reference_range_max',message)
      #else:
        #reference_range_max = reference_range_min
        #line['reference_range_max'] = reference_range_max
    if reference_range_min not in (None,'') and reference_range_max not in (None,''):
      if item_model.isFixedPrice():
        convert_func = convertTravelerCheckReferenceToInt
        value_denomination = 'traveler check reference'
      else:
        convert_func = convertCheckReferenceToInt
        value_denomination = 'check reference'
      try:
        reference_range_min = convert_func(reference_range_min)
      except ValueError:
        generate_error(line, 'reference_range_min', 'This is not a valid %s' % (value_denomination, ))
      try:
        reference_range_max = convert_func(reference_range_max)
      except ValueError:
        generate_error(line, 'reference_range_max', 'This is not a valid %s' % (value_denomination, ))
      if check_amount is not None: # In the case of a check book
        check_amount_relative_url = '/'.join(check_amount.split('/')[1:])
        line['check_amount_relative_url'] = check_amount_relative_url
        check_amount_value = context.getPortalObject().restrictedTraverse(check_amount_relative_url)
        check_quantity = int(check_amount_value.getQuantity())
      else:
        check_quantity = 1
      if same_type(reference_range_min, 0) and \
         same_type(reference_range_max, 0) and \
         (reference_range_max - reference_range_min + 1 != check_quantity * quantity
          or
          reference_range_max < reference_range_min):
        context.log("Range is not valid",
                    "range max %s, range min %s, check quantity %s, quanityt %s" %(reference_range_max,
                                                                                   reference_range_min,
                                                                                   check_quantity, quantity))
        message = 'The range is not valid'
        generate_error(line,'reference_range_min',message)
        generate_error(line,'reference_range_max',message)

for i in xrange(len(listbox), 10):
  listbox.append({'quantity':1})

if batch_mode:
  return (error_value, field_error_dict)
else:
  context.Base_updateDialogForm(listbox=listbox
                             , portal_type = context.getPortalType()
                             , resource=resource
                             , previous_resource=resource
                             ,empty_line_number=0 )
  if field_error_dict != {}:
    request.set('field_errors', field_error_dict)
    kw['REQUEST'] = request
  return context.asContext(  context=None
                             , portal_type = context.getPortalType()
                             , resource=resource
                             , previous_resource=resource
                             ).CheckDetail_viewLineFastInputForm(**kw)
