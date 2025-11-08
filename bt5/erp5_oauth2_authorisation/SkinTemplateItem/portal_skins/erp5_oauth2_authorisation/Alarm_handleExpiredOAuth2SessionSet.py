"""
Cleanup OAuth2 Sessions.

This is not required for expired sessions to be unusable (as they should be),
but this allows cleaning up sessions from a document point of view.
"""
LOAD_LIMIT = 10000
now = DateTime()
container_value = context.getPortalObject().session_module
searchFolder = container_value.searchFolder
deletion_id_list = []
action_tag = script.id + '_action'
deletion_delay_days = context.ERP5Site_getPreferredInvalidatedOAuth2SessionDeletionDelay()
if deletion_delay_days is None:
  deletion_cutoff = None
else:
  deletion_cutoff = now - deletion_delay_days
load_limit = LOAD_LIMIT
action_skip_count = 0
with context.defaultActivateParameterDict({'tag': action_tag}, placeless=True):
  for (state_list, expiration_max_date, action) in (
    ( # Draft sessions' expiration date is the time the Authorisation Code expires.
      # These should be quite rare, as they mean authentication succeeded but was not transformed into a token.
      # The session did not actually become something, so mark it deleted.
      ('draft', ),
      now,
      lambda x: x.delete(),
    ),
    ( # Validated sessions' expiration date, plus the associated client's accuracy, is the time the Refresh Token expires.
      # Invalidate the session, as it is now unusable and should not be presented to the user when listing active sessions.
      ('validated', ),
      # XXX: expects a maximum of one-day expiration max inaccuracy
      now - 1,
      lambda x: x.invalidate(),
    ),
    (
      # Invalidated and deleted (state) sessions get deleted after enough time has passed.
      ('invalidated', 'deleted'),
      deletion_cutoff,
      lambda x: deletion_id_list.append(x.getId()),
    ),
  ):
    if expiration_max_date is None:
      continue
    catalog_date_condition = '<%f' % expiration_max_date.timeTime()
    for state in state_list: # Query with a single state at a time for better SQL index efficiency
      result_list = searchFolder(
        portal_type='OAuth2 Session',
        validation_state=state,
        float_index=catalog_date_condition,
        limit=load_limit,
      )
      load_limit -= len(result_list)
      for session_value in result_list:
        session_value = session_value.getObject()
        # Recheck document data from ZODB
        if (
          session_value.getValidationState() == state and
          session_value.getExpirationDate() <= expiration_max_date
        ):
          action(session_value)
        else:
          action_skip_count += 1
      if load_limit <= 0:
        break
    else:
      continue
    break
  if deletion_id_list:
    container_value.manage_delObjects(ids=deletion_id_list)
if load_limit <= 0:
  if (
    action_skip_count >= LOAD_LIMIT or (
      action_skip_count > 100 and
      action_skip_count > (LOAD_LIMIT - load_limit) / 10
    )
  ):
    # Raise if we are about to respawn and more than 10% of the number of found documents were skipped, but not if the absolute value is under 100, but do if LOAD_LIMIT is less than 100.
    # Possible consequences:
    # - poor performance (every subsequent iteration will load and skip the same documents)
    #   This one may be non-critical, but best to know of, investigate and fix.
    # - infinite iteration (this script will respawn itself, find LOAD_LIMIT documents, process 0, and respawn itself until the in-ZODB conditions become true - which can take months)
    #   This one is more difficult to properly fix, and worth a raise.
    raise RuntimeError('Many documents were matched in catalog but skipped by supposedly-identical condition on ZODB (action_skip_count=%s, load_limit=%s). Please investigate.' % (
      action_skip_count,
      load_limit,
    ))
  # The load quota was exhausted, there may be more to cleanup
  getattr(
    context.activate(
      activity='SQLQueue',
      priority=11,
      after_tag=action_tag,
    ),
    script.id,
  )()
