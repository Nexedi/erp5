"""
Cleanup OAuth2 Sessions.

This is not required for expired sessions to be unusable (as they should be),
but this allows cleaning up sessions from a document point of view.
"""
now = DateTime()
now_catalog_condition = '<%f' % now.timeTime()
container_value = context.getPortalObject().session_module
searchFolder = container_value.searchFolder
deletion_id_list = []
client_lifespan_accuracy_dict = {}
def getSessionAccuracyCompensatedExpirationMaxDate(session_value):
  key = session_value.getSource()
  try:
    lifespan_accuracy = client_lifespan_accuracy_dict[key]
  except KeyError:
    lifespan_accuracy = client_lifespan_accuracy_dict[key] = session_value.getSourceValue().getRefreshTokenLifespanAccuracy() / 86400.
  return session_value.getExpirationDate() + lifespan_accuracy
def getSessionRawExpirationMaxDate(session_value):
  return session_value.getExpirationDate()
deletion_delay_days = context.ERP5Site_getPreferredInvalidatedOAuth2SessionDeletionDelay()
if deletion_delay_days is None:
  deletion_cutoff = None
else:
  deletion_cutoff = now - deletion_delay_days
load_limit = 1000
for (state_list, catalog_date_condition, expiration_max_date, getSessionExpirationMaxDate, action) in (
  ( # Draft sessions' expiration date is the time the Authorisation Code expires.
    # These should be quite rare, as they mean authentication succeeded but was not transformed into a token.
    # The session did not actually become something, so mark it deleted.
    ('draft', ),
    now_catalog_condition,
    now,
    getSessionRawExpirationMaxDate,
    lambda x: x.delete(),
  ),
  ( # Validated sessions' expiration date, plus the associated client's accuracy, is the time the Refresh Token expires.
    # Invalidate the session, as it is now unusable and should not be presented to the user when listing active sessions.
    ('validated', ),
    now,
    now_catalog_condition,
    getSessionAccuracyCompensatedExpirationMaxDate,
    lambda x: x.invalidate(),
  ),
  (
    # Invalidated and deleted (state) sessions get deleted after enough time has passed.
    ('invalidated', 'deleted'),
    (
      None
      if deletion_cutoff is None else
      '<%f' % deletion_cutoff.timeTime()
    ),
    deletion_cutoff,
    getSessionRawExpirationMaxDate,
    lambda x: deletion_id_list.append(x.getId()),
  ),
):
  if now_catalog_condition is None:
    continue
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
        getSessionExpirationMaxDate(session_value) <= expiration_max_date
      ):
        action(session_value)
    if load_limit <= 0:
      break
if deletion_id_list:
  DELETE_CHUNK = 1000
  active_delObjects = container_value.activate(
    activity='SQLQueue',
    priority=10,
  ).manage_delObjects
  while deletion_id_list:
    active_delObjects(ids=deletion_id_list[:DELETE_CHUNK])
    deletion_id_list = deletion_id_list[DELETE_CHUNK:]
if load_limit <= 0:
  # The load quota was exhausted, there may be more to cleanup
  getattr(
    context.activate(
      activity='SQLQueue',
      priority=11,
    ),
    script.id,
  )()
