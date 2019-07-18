"""Create an assignment for the person depending credential request configuration
Proxy: Assignor -- allow to update the related assignment
"""

# check the script is not called from a url
if REQUEST is not None:
  return None

#Initialisation
assignment_duration = context.portal_preferences.getPreferredCredentialAssignmentDuration()
today = DateTime()
delay = today + assignment_duration

person = context.getDestinationDecisionValue(portal_type="Person")
assignment = person.newContent(
        portal_type='Assignment',
        title = '%s Assignment' % (context.getSite('').capitalize()),
        function = ['contributor'], # hard coded and based on security models
        start_date = today - 1,
        stop_date = delay)
assignment.open()
