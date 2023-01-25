# This script uses file= argument
# pylint: disable=redefined-builtin
"""
This script provides a facility to permit conversion by format.
"""

###Below is an example which pure auditors can only view in non editable
### formats (pdf, html, txt, png, etc.)
###
from AccessControl import getSecurityManager
user = getSecurityManager().getUser()
role_list = user.getRolesInContext(context)
##

# Users involved in the document may view it in editable mode
if "Associate" in role_list or "Assignee" in role_list or\
    "Assignor" in role_list or "Manager" in role_list or "Owner" in role_list:
  return True
# Reject original format
if format is None:
  return False
##
# All users with view permission may view the document
# in read only mode
if format in ('html', 'stripped-html', 'text', 'txt', 'pdf', 'png', 'jpg', 'gif'):
  return True
if format.endswith('pdf'):
  return True
if format.endswith('html'):
  return True
##
## # All other formats are prohibitted
return False
