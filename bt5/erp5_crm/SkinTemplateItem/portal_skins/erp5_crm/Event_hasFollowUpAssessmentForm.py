if not context.getFollowUp():
  return False
followup_value = context.getFollowUpValue(checked_permission='Access contents information')
if followup_value is None:
  return False
if getattr(followup_value, 'getAssessmentFormId', None) is None:
  return False
return followup_value.getAssessmentFormId()
