"""
This script notify the user that the form has been submitted
"""
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from AccessControl import getSecurityManager

form = state_change['object']
portal = form.getPortalObject()

translateString = portal.Base_translateString
portal_catalog = portal.portal_catalog



u = getSecurityManager().getUser()
recipient = portal.portal_catalog.getResultValue(portal_type='Person', reference=u)
 

# Build the message and translate it
msg = []

form_id = form.getId()
procedure=translateString(form.getPortalType())


wf_info=form.Egov_getProcedureWorkflowStateInfo('egov_universal_workflow','submitted')
date_of_submission=wf_info['time'].strftime('%d/%m/%y %H:%M')

subject = translateString("[E-government] Your ${procedure} document number: ${form_id} has been submitted", 
                           mapping = dict(procedure=procedure, form_id=form_id))

msg_content=""" 

Your ${procedure} has been transmitted under the reference : ${form_id}, at ${date_of_submission}


E-government TEAM

"""

msg_content = translateString(msg_content,
                              mapping=dict(procedure=procedure, 
                                           form_id=form_id,
                                           date_of_submission=date_of_submission
                                          )
                             )

# We can now notify the accoutant through the notification tool
portal.portal_notifications.sendMessage(recipient=recipient, 
    subject=subject, message=msg_content, portal_type_list=['%s' % form.getPortalType(),],
    store_as_event=True)
