"""
  Check that all datas necessary to auto-calculate the pay sheet are set.
"""
paysheet = context
employer = paysheet.getDestinationSection()
employee = paysheet.getSourceSection()
quantity_unit = paysheet.getWorkTimeAnnotationLineQuantityUnit() # XXX - to refactor

Base_translateString = context.Base_translateString

def redirect(msg):
  return context.Base_redirect(form_id,
      keep_items = dict(portal_status_message=Base_translateString(msg)))

if not paysheet.getPriceCurrency():
  return redirect('Currency must be defined')

if not paysheet.getStartDate():
  return redirect('Work Period Start must be defined')

if not paysheet.getStopDate():
  return redirect('Work Period End must be defined')

if not employee:
  return redirect('The employee must be defined')

if not employer:
  return redirect('The employer must be defined')

if not quantity_unit:
  return redirect('The work duration unit must be defined')

employee_obj = paysheet.getSourceSectionValue()

if not employee_obj.getCareerGrade():
  return redirect('The employee must have a career grade')

if not employee_obj.getMaritalStatusId():
  return redirect('The employee must have a marital status')

context.applyTransformation()
msg = Base_translateString('Pay sheet lines updated.')
return context.Base_redirect('view',
                            keep_items=dict(portal_status_message=msg))
