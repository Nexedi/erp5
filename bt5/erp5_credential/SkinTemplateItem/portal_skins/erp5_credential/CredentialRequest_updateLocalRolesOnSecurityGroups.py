"""After assignment creation/update, the user may have some different security on his person
so it may be updated.
Proxy: Manager -- allow to set password on all account"""

person = context.getDestinationDecisionValue(portal_type="Person")
person.updateLocalRolesOnSecurityGroups()
