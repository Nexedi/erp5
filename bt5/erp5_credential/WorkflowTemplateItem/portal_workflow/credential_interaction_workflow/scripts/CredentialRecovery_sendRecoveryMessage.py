recovery = state_change['object']

if recovery.getReference() is not None:
  recovery.CredentialRecovery_sendPasswordResetLink()
else:
  recovery.CredentialRecovery_sendUsernameRecoveryMessage()
