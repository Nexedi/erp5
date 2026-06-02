if not context.hasUserId():
  context.setUserId(
    'WG%i' % (
      context.getPortalObject().portal_ids.generateNewId(
        id_group='user_id',
        id_generator='non_continuous_integer_increasing',
      ),
    ),
  )

if not context.hasReference():
  context.setReference(
    "WGROUP-%s" % (
      context.getPortalObject().portal_ids.generateNewId(
        id_group='slap_workgroup_reference',
        id_generator='uid',
      ),
    ),
  )
