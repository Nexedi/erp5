# Currently, we set a default group (for the prototype application)
# This should disappear once the application is extended
context.setGroup('dacs/trhc/greffe/civil')
context.setSite('dakar/pikine_guediawaye/tribunal')

# We need to update security now since 
# we just changed the group value and security
# assignment was alreay called. An interaction
# workflow would probably be better or, even 
# simpler, calling updateLocalRolesOnSecurityGroups
# after submission since there is no need for
# Assignor to access drafts.
# XXX Rework needed
context.updateLocalRolesOnSecurityGroups()
