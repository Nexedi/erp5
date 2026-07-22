# Override to customise the retention delay
# Return a delay, in days, OAuth2 Session documents should be kept once they are invalidated (session expired after being fully established) or in deleted state (session expired mid-establishment and was never usable).
# Or None to keep forever.
# This is retroactively applied to existing documents (applied at deletion query-time, not state-change-time)
return None
