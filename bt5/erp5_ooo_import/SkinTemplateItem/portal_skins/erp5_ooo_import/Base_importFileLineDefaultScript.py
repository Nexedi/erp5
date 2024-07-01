#                                   Mohamadou Mbengue <mmbengue@gmail.com>
#
#  This is the Default script used by import module to create spreadshett line's as object
#  With manager role, it's possible to use another script and add specifics changes.
#  In this script the line to create is given as a parameter and is created in an activity
#  witch returns the results of the processing (success=1 if the sstep passes or 0 if not).
#  The result must be be of this format :
#   {
#    'message': translated_msg, ## The translated message of the active process result
#    'object_url': new_object.getRelativeUrl(), ## The url of the object if creation is successfull
#    'object': imported_line, ## Object propeties value's
#    'success': success ## The result of the
#   }
#  The script must have proxy role manager
#####################################################################################################

from ZODB.POSException import ConflictError
from Products.ERP5Type.Message import Message
import six

#Create new ERP5 objects In Activity from OOo document
imported_line = object_url = None

portal = context.getPortalObject()
container = portal.restrictedTraverse(container_relative_url)

portal_type_object = None
for allowed_portal_type in container.allowedContentTypes():
  if portal_type == allowed_portal_type.id:
    portal_type_object = allowed_portal_type
    break

if portal_type_object is None:
  raise ValueError('Disallowed subobject type: %s' % portal_type)
else:
  # Default result
  success = 1
  translated_msg = Message(
       'erp5_ui',
       'Object created successfully - Type: ${portal_type}',
       mapping=dict(portal_type=Message('erp5_ui',
                                        portal_type)))
  imported_line = imported_line_property_dict.copy()

  # Get portal type objects
  base_category_list = portal_type_object.getInstanceBaseCategoryList()

  # Separate categories from properties
  imported_line_category_dict = {}
  for prop_key in list(six.iterkeys(imported_line_property_dict)):
    if prop_key in base_category_list:
      imported_line_category_dict[prop_key] = imported_line_property_dict.pop(prop_key)

  new_object = None
  # Save properties on object
  try:
    new_object = container.newContent(portal_type=portal_type,
                                      **imported_line_property_dict)
  except ConflictError:
    raise
  except Exception as error:
    translated_msg = Message('erp5_ui',
                     'An error Occurred while creating object: ${error}',
                     mapping=dict(error=Message('erp5_ui',
                                                '${error}',
                                                mapping=dict(error=error)))
                     )
    success = 0

  # Save the categories
  for category, value in list(six.iteritems(imported_line_category_dict)):
    category_dict = context.ERP5Site_getCategoriesFullPath(
                                       category_dict={category: value})
    if category_dict not in (None, {}):
      try:
        new_object.edit(**category_dict)
      except ConflictError:
        raise
      except Exception as error:
        #context.log('category: %s' %category)
        translated_msg = Message(
                     'erp5_ui',
                     'An error Occurred while importing the category ${category} - ${error}',
                     mapping=dict(category=Message('erp5_ui',
                                                   '${category}',
                                                   mapping=dict(category=category)),
                                  error=Message('erp5_ui',
                                                '${error}',
                                                mapping=dict(error=error))))
        success = 0
        # Delete the object if error occurs
        #container.manage_delObjects([new_object.getId()])
      del imported_line_category_dict[category]

  # Not found categories
  if imported_line_category_dict not in ({}, None):
    value_list = ', '.join(imported_line_category_dict.values())
    category_list = ', '.join(imported_line_category_dict.keys())

    translated_msg = Message('erp5_ui',
           'An error occured, values ("${value_list}") not found in categories ("${category_list}")',
           mapping=dict(value_list=value_list, category_list=category_list))
    success = 0

  if not success:
    # Delete the object if error occurs
    # FIXME: maybe this should be an option ?
    container.manage_delObjects([new_object.getId()])

  return {
    'message': translated_msg,
    'object_url': new_object.getRelativeUrl(),
    'object': imported_line,
    'success': success
  }
