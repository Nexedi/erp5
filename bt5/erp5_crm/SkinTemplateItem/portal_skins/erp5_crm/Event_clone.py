event = context.Base_createCloneDocument(batch_mode=True)
event.setFollowUp(follow_up_relative_url)
return event
