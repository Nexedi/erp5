Base_translateString = context.Base_translateString
paysheet = context

# copy categories
category_list = [
  'destination_section', 'source_section', 'source_payment',
  'destination_payment', 'price_currency',
]
new_category_dict = {}

specialise_value = paysheet.getSpecialiseValue()
if specialise_value is None:
  model = None
else:
  model = specialise_value.getEffectiveModel(
    start_date=paysheet.getStartDate(),
    stop_date=paysheet.getStopDate()
  )

if model is None:
  return context.Base_redirect(form_id,
     keep_items=dict(portal_status_message=Base_translateString('No pay sheet model.')))

for category in category_list:
  if force or not paysheet.getPropertyList(category):
    v = model.getModelInheritanceEffectiveProperty(paysheet, category)
    if v:
      new_category_dict[category] = v

# copy the price_currency into the ressource :
price_currency = model.getModelInheritanceEffectiveProperty(paysheet, 'price_currency')
if price_currency:
  new_category_dict['resource'] = price_currency
  new_category_dict['price_currency'] = price_currency

def copyPaymentCondition(paysheet, model):
  filter_dict = {'portal_type': 'Payment Condition'}
  effective_model_list = model.findEffectiveSpecialiseValueList(paysheet)
  for effective_model in effective_model_list:
    to_copy = effective_model.contentIds(filter=filter_dict)
    if len(to_copy) > 0 :
      copy_data = effective_model.manage_copyObjects(ids=to_copy)
      paysheet.manage_pasteObjects(copy_data)

filter_dict = {'portal_type': 'Payment Condition'}
if force:
  paysheet.manage_delObjects(list(paysheet.contentIds(filter=filter_dict)))
if len(paysheet.contentIds(filter=filter_dict)) == 0:
  copyPaymentCondition(paysheet, model)

# copy model sub objects into paysheet
paysheet.PaySheetTransaction_copySubObject(
                  portal_type_list=('Annotation Line',),
                  property_list=('quantity', 'source', 'resource'))
paysheet.PaySheetTransaction_copySubObject(
                  portal_type_list=('Pay Sheet Model Ratio Line',),
                  property_list=('quantity',))
paysheet.PaySheetTransaction_copySubObject(
                  portal_type_list=('Payment Condition',))

paysheet.edit(**new_category_dict)

if not batch_mode:
  return context.Base_redirect(form_id,
                   keep_items=dict(portal_status_message=\
                       Base_translateString('Pay sheet transaction updated.')))
