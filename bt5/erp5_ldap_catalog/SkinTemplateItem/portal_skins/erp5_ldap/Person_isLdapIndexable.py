return context.getPortalType() == 'Person' \
and context.getReference() is not None \
and context.getPassword() is not None \
and context.getFirstName() is not None \
and context.getLastName() is not None \
and context.getDefaultEmailText() is not None
