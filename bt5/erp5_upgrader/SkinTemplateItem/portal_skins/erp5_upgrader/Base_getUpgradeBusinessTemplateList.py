"""
This script may be overridden.
It is expected to return two lists of Business Templates:
- The first is a tuple containing names of Business Templates to install and
  keep up-to-date. Their dependencies are also installed and kept up-to-date.
- The second is a list containing names of Business Templates which should be
  kept if already installed, ignored if missing, and not be upgraded nor
  removed.
"""
return (
  tuple(context.getPortalObject().getCoreBusinessTemplateList() + ['erp5_base']),
  ['erp5_upgrader'],
)
