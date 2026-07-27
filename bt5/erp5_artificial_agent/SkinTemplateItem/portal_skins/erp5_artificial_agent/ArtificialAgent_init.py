# Type init_script for the Artificial Agent portal type, mirror of erp5_base
# Person_init: initialise the user id when the object is created.
#
# NOTE (security policy, CLAUDE.md): the erp5_base Person_init script carries
# _proxy_roles ('Manager', 'Owner') so a low-privilege creator can still mint
# the user id. Per the non-negotiable workspace policy no _proxy_roles element
# is set on this script. If minting a user id for an Artificial Agent genuinely
# requires elevated rights for the expected creators, that must be authorised
# by Cedric / Jean-Paul Smets rather than added silently. See PLAN.md D2 and
# the slice report.
context.initUserId()
