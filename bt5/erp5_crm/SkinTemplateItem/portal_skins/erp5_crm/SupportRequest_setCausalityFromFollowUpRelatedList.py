if context.hasCausality():
  return
event_list = context.getFollowUpRelatedValueList()
event_list.sort(key=lambda x:x.getStartDate())
if len(event_list):
  context.setCausalityValue(event_list[0])
