"""Just an alias for real script
"""
from Products.ERP5Type.Log import log
log('DeprecationWarning: Please use Document_getStandardFilename')
return context.Document_getStandardFilename(format=format)
