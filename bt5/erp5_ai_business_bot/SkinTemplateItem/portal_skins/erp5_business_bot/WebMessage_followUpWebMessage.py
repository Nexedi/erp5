# This script creates a new ticket object from this current event based on its tags
translateString = context.Base_translateString
portal = context.getPortalObject()
current_object = context.getObject()

if tags == None:
  return()
assign = None #

# Find appropriate ticket type
tagset = set(tags)
so = {"sale", "pricing", "demo", "partnership", "advertising"}
sr = {"help", "starting", "install", "bug"}
m = {"job", "sponsorship", "academic", "contributor"}

if tagset.intersection(sr):
  module = context.getPortalObject().support_request_module
  ticket_type = "Support Request"
elif tagset.intersection(so):
  module = context.getPortalObject().sale_opportunity_module
  ticket_type = "Sale Opportunity"
else:
  module = context.getPortalObject().meeting_module
  ticket_type = "Meeting"

if not portal.Base_checkPermission(module.getId(), "Add portal content"):
  return context.Base_redirect(
    form_id,
    keep_items=dict(
      portal_status_message=translateString(
        "You do not have permission to add new ticket.")
    )
  )

# Create a new object
new_id = str(module.generateNewId())
context.portal_types.constructContent(
        type_name=ticket_type,
        container=module,
        id=new_id
)
new_object = module[new_id]

# If we do this before, each added line will take 20 times more time
# because of programmable acquisition
new_object.edit(
        title=current_object.getTitle(),
        destination_decision_list=current_object.getSourceList(),
        source_decision_list=current_object.getDestinationList(),
        start_date=current_object.getStartDate()
)
# Now create the relation between the current object and the new one
current_object.setFollowUpValueList([new_object])
if assign:
  new_object.setSourceTrade([assign[1]])

# Redirect to new object
if assign == None:
  message = translateString(
    "Created and associated a new ${ticket_type} for ${title}.  Here is a recommended response.", 
    mapping=dict(ticket_type = translateString(ticket_type), title = current_object.getTitle()))
  return current_object.Base_redirect('WebMessage_viewCreateResponseDialog', keep_items={'portal_status_message': message})

else:
  name = assign[0]
  message = translateString(
    "Created and associated a new ${ticket_type} for ${title}.  " + name + " is recommended to handle it", 
    mapping=dict(ticket_type = translateString(ticket_type), title = current_object.getTitle()))
  return new_object.Base_redirect('view', keep_items={'portal_status_message': message})
