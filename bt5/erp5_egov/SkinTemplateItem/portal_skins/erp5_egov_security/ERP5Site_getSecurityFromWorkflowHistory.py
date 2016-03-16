"""
This script returns a list of dictionaries which represent
the security groups which a person is member of. It extracts
the categories from the current content. It is useful in the
following cases:

- calculate a security group based on a given
  category of the current object (ex. group). This
  is used for example in ERP5 DMS to calculate
  document security.

- assign local roles to a document based on
  the person which the object related to through
  a given base category (ex. destination). This
  is used for example in ERP5 Project to calculate
  Task / Task Report security.

The parameters are

  base_category_list -- list of category values we need to retrieve
  user_name          -- string obtained from getSecurityManager().getUser().getId()
  object             -- object which we want to assign roles to
  portal_type        -- portal type of object

NOTE: for now, this script requires proxy manager
"""

portal_workflow = context.getPortalObject().portal_workflow

history_list = context.portal_workflow.getInfoFor(ob=context, 
                                          name='history', wf_id='egov_universal_workflow')

last_site, last_group, last_function, last_user = (None, None, None, None)
result = []
for history_line in history_list:
  if history_line.has_key('assigned_group') and history_line['assigned_group']:
    last_group = history_line['assigned_group']
    last_function = history_line['assigned_function']
    last_site = history_line['assigned_site']
    result.append(
          {'function': last_function,
           'group': last_group,
           'site': last_site}
    )
  if history_line.has_key('assigned_user') and history_line['assigned_user']:
    result.append(
      {'group': last_user}
    )

return result
