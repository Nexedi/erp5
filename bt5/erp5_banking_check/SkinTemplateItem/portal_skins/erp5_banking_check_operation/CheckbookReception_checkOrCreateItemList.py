# It was decided that it is possible to receive in an agency only
# checks and checkbooks for accounts managed by that agency. Moreover
# we have decided that we will not allow many checkbook reception at
# a time inside an agency, like this we can create many activities with
# the tag "CheckbookReception_[Agency Code or Url]" in order to make sure
# we will not do duplicate (of course we check that there is not already
# a check or checkbook with this references.

from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

destination_id = context.getDestinationId()
if destination_id is None:
  msg = Message(domain='ui', message='Sorry, you must define the site')
  raise ValidationFailed(msg,)

# serialize destination vault to only have one operation at a time
destination_value = context.getDestinationValue()
destination_value.serialize()
line_list = context.objectValues(portal_type='Checkbook Reception Line')

for line in line_list:
  if not line.getResourceValue().isUniquePerAccount():
    checkbook_reception_tag = "CheckbookReception_global"
    msg = Message(domain='ui', message='Sorry, there is already a pending checkbook reception')
    break
else:
  msg = Message(domain='ui', message='Sorry, there is already a checkbook reception newly validated')
  checkbook_reception_tag = "CheckbookReception_%s" % destination_id
if context.portal_activities.countMessageWithTag(checkbook_reception_tag) != 0:
  raise ValidationFailed(msg,)

if check == 1:
  encountered_check_identifiers_dict = {}
  for line in line_list:
    encountered_check_identifiers_dict = line.CheckbookReceptionLine_checkOrCreateItemList(check=1, 
         encountered_check_identifiers_dict=encountered_check_identifiers_dict)

if create==1:
  for line in line_list:
    line.activate(priority=4, tag=checkbook_reception_tag).\
        CheckbookReceptionLine_checkOrCreateItemList(create=1, tag=checkbook_reception_tag, confirm_check=confirm_check)
