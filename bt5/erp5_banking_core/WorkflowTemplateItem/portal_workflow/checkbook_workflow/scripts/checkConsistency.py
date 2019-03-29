from Products.DCWorkflow.DCWorkflow import ValidationFailed
object = state_change['object']
N_ = object.Base_translateString

check_result = object.checkConsistency()

if len(check_result) > 0:
  check_type    = N_(check_result[0][-1])
  # TODO: use nice url encoding method there instead of replace()
  check_details = check_result[0][-2].replace('<', '&lt;').replace('>', '&gt;')
  raise ValidationFailed("%s : %s" % (check_type, check_details))
