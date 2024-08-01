holiday_acquisition = context.getCausalityRelatedValue(
    portal_type='Holiday Acquisition')

if holiday_acquisition:
  message = context.Base_translateString('Holiday Acquisition is already created')
  return holiday_acquisition.Base_redirect('view', keep_items={
    'portal_status_message': message})


return context.Base_redirect('view',keep_items={'portal_status_message': \
      context.Base_translateString('Holiday Acquisition not found')})
