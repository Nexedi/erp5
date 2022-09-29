"""
  This script tries to produce a thumbnail for any
  document which supports thumbnails. If more document
  types provide a thumbnail, this script must be extended.

  TODO:
  - this should be part of the Document class API ?
  - display of thumbnail must be configurable (yes/no, size)
    ideally with some AJAX  in listbox ?
  - pregenerate thumbails (as part of Document API too, for example
    in relation with metadata discovery, within an activity)
"""
portal_type = context.getPortalType()

if portal_type in ('Drawing', 'Image', 'PDF', 'Presentation', 'Spreadsheet', 'Text', 'Web Page'):
  return context.absolute_url()

if portal_type in ('Person', 'Organisation', 'Credential Update', \
                    'Component', 'Product',) and context.getDefaultImageAbsoluteUrl() is not None:
  return context.getDefaultImageAbsoluteUrl()

return None
