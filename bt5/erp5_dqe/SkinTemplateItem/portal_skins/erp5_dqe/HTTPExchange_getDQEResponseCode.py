response = context.getResponse()
if response == 'TIMEOUT':
  return 'Timeout'
elif response == 'FAILURE':
  return context.Base_translateString('Failure')
return context.HTTPExchange_getDQEResponseDict().get(
  context.Base_getDQEServiceToErrorKeyDict()[context.getResourceValue()], ''
)
