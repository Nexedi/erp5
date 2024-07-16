from erp5.component.document.Document import ConversionError
from erp5.component.module.Log import log
from ZODB.POSException import ConflictError
from six.moves.xmlrpc_client import Fault
from socket import error as SocketError

message = None
if context.getExternalProcessingState() not in ('converted', 'empty'):
  # try to convert to base format only if not already done
  try:
    return context.convertToBaseFormat()
  except ConflictError:
    raise
  except ConversionError as e:
    message = 'Conversion Error: %s' % (str(e) or 'undefined.')
  except Fault as e:
    message = 'XMLFault: %s' % (repr(e) or 'undefined.')
  except SocketError as e:
    message = 'Socket Error: %s' % (repr(e) or 'undefined.')
  except Exception as e:
    message = 'Problem: %s' % (repr(e) or 'undefined.')
  # reach here, then exception was raised, message must be logged in workflow
  # do not simply raise but rather change external processing state
  # so user will see something is wrong
  context.conversionFailed(comment=message)
  log('%s %s' %(context.getRelativeUrl(), message))
return message
