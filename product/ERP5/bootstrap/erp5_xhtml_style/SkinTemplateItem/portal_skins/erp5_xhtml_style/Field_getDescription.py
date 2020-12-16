from Products.ERP5Type.Cache import CachingMethod

field = context
field_id = field.getId()
form = field.aq_parent
form_id = form.getId()
document = form.aq_parent
if getattr(document, 'getPortalType', None) is None:
  document = None

def getFieldDescription(field_id):
  desc = field.get_value('description')
  if desc in ('', None):
    split_id = field_id.split('_', 1)
    if split_id[0] == 'my':
      if document is None:
        desc = 'Dummy field description for %s' % (field_id, )
      else:
        try:
          properties = document.propertyMap()
        except AttributeError: # If context has no propertyMap, give up
          properties = []
        for prop in properties:
          if split_id[1] == prop['id']:
            desc = prop.get('description', '')
            break
  return desc

if document is not None:
  getFieldDescription = CachingMethod(getFieldDescription, ('getFieldDescription', form_id), \
                                      cache_factory='erp5_ui_long')
return getFieldDescription(field_id)
