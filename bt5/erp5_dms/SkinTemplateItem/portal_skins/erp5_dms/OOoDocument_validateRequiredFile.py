"""
  This script is called at file upload time as an external validator.
  It is meant to check that a file was provided in the upload field
  of the upload dialog.
"""
# XXX-JPS should be moved to File_validateRequiredFile and used everywhere
return not(value is None or not value)
