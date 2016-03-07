"""
  This simple script returns the contributor title list of the current context.
  It has a proxy_role of manager to allowed anonymous to get the contributor title
"""

return len(context.getContributorTitleList()) and context.getContributorTitleList() or [context.Base_translateString("Unknown User")]
