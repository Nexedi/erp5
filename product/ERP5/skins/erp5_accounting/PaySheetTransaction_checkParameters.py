## Script (Python) "PaySheetTransaction_checkParameters"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
paysheet      = context.getObject()
paysheet_type = paysheet.getPortalType()

employee      = paysheet.getDestinationSection()
employer      = paysheet.getSourceSection()

if paysheet.getGrossSalary() == None:
  return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=Gross+salary+is+required')

if employee in ('', None):
  return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=The+employee+is+required')

if employer in ('', None):
  return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=The+employer+is+required')

employee_obj  = paysheet.getDestinationSectionValue()
employer_obj  = paysheet.getSourceSectionValue()

if employee_obj.getCareerGrade() in ('', None):
  return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=The+employee+must+have+a+career+grade')

if employer_obj.getCreationDate() in ('', None):
  return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=The+employer+must+have+an+organisation+creation+date')

if employer_obj.getDefaultAddress().getZipCode() in ('', None):
  return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=The+employer+must+have+a+zip+code')

# parameters are OK, go to the pre-calculation form
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + "/PaySheetTransaction_viewPreview?selection_name=default&amp;dialog_category=object_action&amp;form_id=PaySheetTransaction_view")
