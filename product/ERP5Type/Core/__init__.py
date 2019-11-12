# Make sure CMFCategory product is imported before ERP5Type.Core.Folder
# because Folder needs PropertySheet.CategoryCore
# This is important for ZEO server which may need to import conflict-resolution
# classes from products that depend (at 'import' time) directly on Folder.
try:
  import Products.CMFCategory
except ImportError:
  pass
