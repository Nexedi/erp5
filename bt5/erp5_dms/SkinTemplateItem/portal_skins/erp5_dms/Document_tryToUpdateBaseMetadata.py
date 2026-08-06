from ZODB.POSException import ConflictError
from erp5.component.document.Document import ConversionError
from erp5.component.module.Log import log

message = None
try:
  return context.updateBaseMetadata(**kw)
except ConflictError:
  raise
except ConversionError as e:
  message = 'Conversion Error: %s' % (str(e) or 'undefined.')
except Exception as e:
  message = 'Problem: %s' % (repr(e) or 'undefined.')

log('%s %s' %(context.getRelativeUrl(), message))
return message
