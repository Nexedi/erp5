# Type-based hook for user-id minting, resolved by Person.initUserId() through
# self.getTypeBasedMethod('initUserId') -> ArtificialAgent_initUserId.
#
# Mirrors the built-in Person.initUserId body (document.erp5.Person) but mints
# a user id with an 'A' prefix so Artificial Agent user ids are distinguishable
# from Person ('P') user ids (PLAN.md 4.1). setUserId() routes through
# Person._setUserId, which performs the same user-id-availability check as the
# built-in path, so no private (name-mangled) helper is needed here.
if context.hasUserId():
  return context.getUserId()
portal = context.getPortalObject()
user_id = 'A%i' % portal.portal_ids.generateNewId(
    id_group='user_id',
    id_generator='non_continuous_integer_increasing',
)
context.setUserId(user_id)
context.reindexObject()
return user_id
