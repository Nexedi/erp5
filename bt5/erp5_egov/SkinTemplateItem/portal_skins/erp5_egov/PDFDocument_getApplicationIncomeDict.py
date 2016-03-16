'''
  return the dict of the possible attached files
'''
require = ['Optional', 'Required']
attachment_count = 39
attachement_type_dict = {}
portal_type_object = context.getTypeInfo()

if portal_type_object.getStepAttachment():
  for i in range(attachment_count+1)[1:]:
    title = getattr(portal_type_object, "getAttachmentTitle%s" % i, None)
    requirement = getattr(portal_type_object, "getAttachmentRequired%s" % i, None)
    attachment = getattr(portal_type_object, "getAttachmentJustificative%s" % i, None)
    type = getattr(portal_type_object, "getAttachmentModel%s" % i, None)
    if type is not None:
      type = type()
      attachement_format = '   Format :  %s' % type
    else:
      type = []
    if requirement is not None and requirement() is not None:
      required = require[requirement()]
    if title is not None and title()!="" and attachment is not None and attachment():
      attachement_type_dict[title()] = {
           'description': attachement_format,
           'requirement': required,  
           'outcome'    : False,
           'type'       : type,
      }

return attachement_type_dict
