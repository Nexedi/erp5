"""
Cleanup OAuth2 Sessions.

This is not required for expired sessions to be unusable (as they should be),
but this allows cleaning up sessions from a document point of view.
"""
now = DateTime()
now_catalog_condition = '<%f' % now.timeTime()
container_value = context.getPortalObject().session_module
searchFolder = container_value.searchFolder
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
for (state, expiration_max_date, getSessionExpirationMaxDate, action) in (
  ( # Draft sessions' expiration date is the time the Authorisation Code expires.
    # These should be quite rare, as they mean authentication succeeded but was not transformed into a token.
    # The session did not actually become something, so mark it deleted.
    'draft',
    now,
    getSessionRawExpirationMaxDate,
    lambda x: x.delete(),
  ),
  ( # Validated sessions' expiration date, plus the associated client's accuracy, is the time the Refresh Token expires.
    # Invalidate the session, as it is now unusable and should not be presented to the user when listing active sessions.
    'validated',
    now,
    getSessionAccuracyCompensatedExpirationMaxDate,
    lambda x: x.invalidate(),
  ),
):
  for session_value in searchFolder(
    portal_type='OAuth2 Session',
    validation_state=state,
    float_index=now_catalog_condition,
  ):
    session_value = session_value.getObject()
    # Recheck document data from ZODB
    if (
      session_value.getValidationState() == state and
      getSessionExpirationMaxDate(session_value) <= expiration_max_date
    ):
      action(session_value)
