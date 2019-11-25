"""Script to execute `workflow_action`on selected documents by `listbox_uid` with optional `comment`.

This script is intended as a dialog target.

:param form_id, dialog_id: mandatory parameters of dialog form target script
:param listbox_uid: {list[int]} marks that this script takes objects from previous listbox as its input
:param mass_workflow_action: {str} the ID of (worflow) action to execute on each object
"""

portal = context.getPortalObject()
request = kwargs.get("REQUEST", None) or context.REQUEST
translate = portal.Base_translateString

if not mass_workflow_action:
  return context.Base_redirect(form_id,
                               keep_items={
                                 "portal_status_message": translate("No state change possible on selected documents."),
                                 "portal_status_level": "error"})

# previous_mass_workflow_action is a control field to remember which workflow_action was rendered
# and we disallow submit if different action is selected and different dialog embedded
request.form['field_your_previous_mass_workflow_action'] = mass_workflow_action
# XXX This is hardcoded for the hidden field inside Base_viewWorkflowActionDialog
request.form['field_workflow_form_your_workflow_action'] = mass_workflow_action
# XXX This is hardcoded for the hidden field inside BaseWorkflow_viewWorkflowActionDialog
request.form['field_workflow_form_my_workflow_action'] = mass_workflow_action

if update_method or (previous_mass_workflow_action != mass_workflow_action):
  return context.Base_renderForm(dialog_id,
                                 message=translate("Form updated."),
                                 level="warning",
                                 REQUEST=request)

# generate a random tag for activity grouping
tag = 'folder_workflow_action_{:d}'.format(random.randint(0, 1000))  # Kato: how come that random is accessible?
# We want change state activities to have a lower priority that erp5_deferred_style reports
# not to prevent everybody from running report while a users change state of many documents.
priority = 3
batch_size = 100

workflow_action_kwargs = workflow_form.as_dict()
workflow_action_kwargs['workflow_action'] = mass_workflow_action
workflow_action_kwargs['batch_mode'] = True

portal.portal_catalog.searchAndActivate(
  uid=listbox_uid,
  method_id='Base_workflowStatusModify',
  activate_kw={'tag': tag, 'priority': priority},
  packet_size=batch_size,
  method_kw=workflow_action_kwargs
)

# activate something on the module after everything, so that user can know that
# something is happening in the background
context.activate(after_tag=tag).getId()

return context.Base_redirect(form_id,
  keep_items=dict(portal_status_message=translate("Workflow modification in progress.")))
