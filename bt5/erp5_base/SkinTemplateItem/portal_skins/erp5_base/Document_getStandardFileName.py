# this script has an `format` argument
# pylint: disable=redefined-builtin
"""Just an alias for real script
"""
from erp5.component.module.Log import log
log('DeprecationWarning: Please use Document_getStandardFilename')
return context.Document_getStandardFilename(format=format)
