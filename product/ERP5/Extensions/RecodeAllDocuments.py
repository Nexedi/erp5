from Products.ERP5Type.Globals import get_request
from Acquisition import aq_base
from Products.ERP5Type.Base import Base
from zLOG import LOG

message = ''

def recodeDocumentRecursively(document, dry_run=0):
  global message

  klass = document.__class__
  if not issubclass(klass, Base):
    return

  id_list = []
  for property_sheet in klass.property_sheets:
    for property in property_sheet._properties:
      # Do not care about tokens, int, float, date or boolean because they should not have non-ASCII.
      if property['type'] in ('string', 'text', 'lines') and 'acquisition_base_category' not in property:
        id = property.get('storage_id', property['id'])
        # Make sure that ids are not duplicated.
        if id not in id_list:
          id_list.append(id)

  # Make sure working on the document itself.
  base = aq_base(document)
  for id in id_list:
    #LOG('RecodeAllDocuments', 0, 'Recoding %s of %s' % (id, document.getRelativeUrl()))
    value = getattr(base, id, None)
    if value is not None:
      if type(value) == type(''):
        if len(value) > 0:
          message += 'Recoding %s of %s\n' % (id, document.getRelativeUrl())
          if not dry_run: setattr(base, id, unicode(value, 'iso-8859-1').encode('utf-8'))
      elif type(value) in (type(()), type([])):
        if len(value) > 0:
          value_list = list(value)
          for i in range(len(value_list)):
            value = value_list[i]
            if type(value) == type('') and len(value) > 0:
              value_list[i] = unicode(value, 'iso-8859-1').encode('utf-8')
          message += 'Recoding %s of %s\n' % (id, document.getRelativeUrl())
          if not dry_run: setattr(base, id, tuple(value_list))
      else:
        raise RuntimeError, 'unknown type of value %r' % value

  # Call itself recursively.
  for object in document.objectValues():
    recodeDocumentRecursively(object)

def recodeAllDocuments(self, REQUEST=None, dry_run=0):
  global message
  message = ''

  if not REQUEST:
    REQUEST = get_request()

  try:
    dry_run = int(dry_run)
  except:
    pass

  portal = self.getPortalObject()
  #for folder in portal.objectValues('ERP5 Folder'):
  #  message += '# Checking the folder %s\n' % folder.getId()
  #  recodeDocumentRecursively(folder, dry_run=dry_run)
  for category in portal.portal_categories.objectValues('ERP5 Base Category'):
    message += '# Checking the category %s\n' % category.getId()
    recodeDocumentRecursively(category, dry_run=dry_run)
  return message