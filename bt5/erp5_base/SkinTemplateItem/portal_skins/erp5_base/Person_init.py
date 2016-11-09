# this script can be overridden as you wish.
if not context.hasReference():
  context.setReference(
    'P%i' % (
      context.getPortalObject().portal_ids.generateNewId(
        id_group='Person.reference',
        id_generator='non_continuous_integer_increasing',
      ),
    ),
  )
