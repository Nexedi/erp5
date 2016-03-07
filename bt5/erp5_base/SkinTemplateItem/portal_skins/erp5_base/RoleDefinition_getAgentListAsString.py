"""
   Used by Base_viewLocalPermissionList to display all agents set locally
   (by adding Role Definition objects) and their roles, in a listbox.
"""
return ', '.join(context.getAgentTitleList([]))
