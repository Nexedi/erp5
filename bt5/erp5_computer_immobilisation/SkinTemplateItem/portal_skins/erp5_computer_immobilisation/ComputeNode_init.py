if not context.hasUserId():
  context.setUserId(
    'C%i' % (
      context.getPortalObject().portal_ids.generateNewId(
        id_group='user_id',
        id_generator='non_continuous_integer_increasing',
      ),
    ),
  )
