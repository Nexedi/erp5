from ZODB.POSException import ConflictError
from Products.ERP5.Document.Document import ConversionError
from Products.ERP5Type.Log import log

message = None
try:
  return context.updateBaseMetadata(**kw)
except ConflictError:
  raise
except ConversionError, e:
  message = 'Conversion Error: %s' % (str(e) or 'undefined.')
except Exception, e:
  message = 'Problem: %s' % (repr(e) or 'undefined.')
except:
  message = 'Problem: unknown'

# reach here, then exception was raised, message must be logged in workflow
# do not simply raise but rather change external processing state
# so user will see something is wrong. As usually updateBaseMetadata is called
# after convertToBaseFormat it's possible that object is in conversion failed state 
isTransitionPossible = context.getPortalObject().portal_workflow.isTransitionPossible
if isTransitionPossible(context, 'conversion_failed'):
  # mark document as conversion failed if not already done by convertToBaseFormat
  context.conversionFailed(comment=message)
else:
  # just save problem message in workflow history
  context.processConversionFailed(comment=message)
log('%s %s' %(context.getRelativeUrl(), message))
return message
