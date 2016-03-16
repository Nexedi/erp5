"""
This script tries to send a message to the appropriate recipient
from the appropriate sender. It uses portal_notifications
and the getObject API of ERP5Catalog.
This script has a proxy role to make sure we can find person documents in the
catalog.
"""
from Products.ERP5Type.Log import log

object = sci['object']
portal = sci.getPortal()
translateString = portal.Base_translateString
portal_catalog = portal.portal_catalog

# Get the owner
owner = object.getViewPermissionOwner()
owner_value = portal_catalog.getResultValue(portal_type='Person', reference=owner)

# Get the authenticated user
user = portal.portal_membership.getAuthenticatedMember().getUserName()
user_value = portal_catalog.getResultValue(portal_type='Person', reference=user)

# If users are not defined, we need to log and return
if not owner or owner_value is None:
  # We keep a trace because this is the best we
  # can do (preventing answers is even worse)
  log("ERP5 Query Workflow", "No owner defined")
  return
if not user or user_value is None:
  # We keep a trace because this is the best we
  # can do (preventing answers is even worse)
  log("ERP5 Query Workflow", "Current user is not defined")
  return

# Build the message and translate it
subject = translateString("Query was answered.")
msg = """The Query ID ${id} which you posted has been answered by ${user}

Question:

${question}

Answer:

${answer}
""" 
msg = translateString(msg, 
             mapping=dict(id=object.getId(),
                          subject=subject,
                          user=user_value.getTitle(),
                          question=object.getDescription(),
                          answer=object.getTextContent())
            )

# We can now notify the owner through the notification tool
portal.portal_notifications.sendMessage(
         sender=user, recipient=owner, subject=subject, message=msg)
