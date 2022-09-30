from Products.ERP5Type.Errors import ImmobilisationCalculationError, ImmobilisationValidityError

immo_period_list = []
error = ''
try:
  immo_period_list = context.getImmobilisationPeriodList()
except ImmobilisationCalculationError:
  error = 'A calculation error occured'
except ImmobilisationValidityError:
  error = 'A movement validity error occured'

if return_errors:
  return context.Base_translateString(error)

immo_object_list = []
for immo_period in immo_period_list:
  immo_object_list.append(context.asContext(**immo_period))
return immo_object_list
