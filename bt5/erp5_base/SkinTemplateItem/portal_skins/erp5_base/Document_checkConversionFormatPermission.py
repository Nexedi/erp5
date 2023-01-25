# this script has an `format` argument
# pylint: disable=redefined-builtin
"""
This script provides a facility to permit conversion by format.
"""
#
# By default, all formats are permitted.
#
return 1


###
### Below is an example which pure auditors can only view in non editable
### formats (pdf, html, txt, png, etc.)
###
## from AccessControl import getSecurityManager
## user = getSecurityManager().getUser()
## role_list = user.getRolesInContext(context)
##
## # Users involved in the document may view it in editable mode
## if "Associate" in role_list or "Assignee" in role_list or\
##    "Assignor" in role_list or "Manager" in role_list or "Owner" in role_list:
##   return 1
##
## # Reject original format
## if format is None:
##   return 0
##
## # All users with view permission may view the document
## # in read only mode
## if format in ('html', 'stripped-html', 'text', 'txt', 'pdf', 'png', 'jpg', 'gif'):
##   return 1
## if format.endswith('pdf'):
##   return 1
## if format.endswith('html'):
##   return 1
##
## # All other formats are prohibitted
## return 0
