configuration_save_url = kw.get('configuration_save_url', None)
user_number = kw.get('user_number', 1)
next_transition = context.getNextTransition().getRelativeUrl()

if user_number > 1:
  # mark next transition  as multiple
  context.setMultiEntryTransition(next_transition, user_number)
else:
  # explicitly reset next transition as not multiple because
  # we may have already set it as multiple
  context.setMultiEntryTransition(next_transition, 0)

# store globally
context.setGlobalConfigurationAttr(user_number=user_number)
