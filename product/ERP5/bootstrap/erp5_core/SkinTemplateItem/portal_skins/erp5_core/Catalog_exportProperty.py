# Script to download XML properties for erp5 catalog

REQUEST = context.REQUEST
RESPONSE = context.REQUEST.RESPONSE

return context.manage_exportProperties(REQUEST, RESPONSE)
