# Run a first batch of calcul in activity
# Then call the report in a deferred mode
from json import dumps
from Products.CMFActivity.ActiveResult import ActiveResult
portal = context.getPortalObject()
N_ = portal.Base_translateString
# Check deferred style is present
if not 'Deferred' in portal.portal_skins.getSkinSelections():
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("Deferred style must be installed to run this report")))
  
person_value = portal.ERP5Site_getAuthenticatedMemberPersonValue()
if person_value is None:
  portal.changeSkin(None)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("No person found for your user")))

if person_value.getDefaultEmailText('') in ('', None):
  portal.changeSkin(None)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("You haven't defined your email address")))

parameter_dict, stat_columns, selection_columns = context.OrderModule_getOrderReportParameterDict()

active_process = context.OrderModule_activateGetOrderStatList(tag=script.id, **parameter_dict)

# Create a result to store computed parameter for later
active_process.postResult(ActiveResult(
  sevrity=1,
  detail=dumps({
      'type' : 'parameters',
      'params' : parameter_dict,
      'stat_columns' : stat_columns,
      'selection_columns' : selection_columns,
      })
      ))

request = context.REQUEST
context.getPortalObject().portal_skins.changeSkin("Deferred")
request.set('portal_skin', "Deferred")
assert deferred_portal_skin is not None, "No deferred portal skin found in parameters"
request.set('deferred_portal_skin', deferred_portal_skin)

kw['deferred_style'] = 1
kw['active_process'] = active_process.getPath()
request.set('active_process', active_process.getPath())
kw.update(parameter_dict)
kw.pop('format',None)
return context.Base_activateReport(
  form = getattr(context, report_method_id),
  after_tag=script.id,
  **kw
  )
