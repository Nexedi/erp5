request = context.REQUEST
site = context.getPortalObject()
Base_translateString = site.Base_translateString
error_message = None
uids = site.portal_selections.getSelectionCheckedUidsFor(selection_name)
if len(uids) != 2:
  error_message =  Base_translateString("Please select one publication and one subscription.")

object_list = [x.getObject() for x in site.portal_catalog(uid=uids)]

pub = None
sub = None
r1 = object_list[0]
if r1.getPortalType() == "SyncML Publication":
  pub = r1
else:
  sub = r1

r2 = object_list[1]
if r2.getPortalType() == "SyncML Publication":
  pub = r2
else:
  sub = r2

if not pub or not sub:
  error_message =  Base_translateString("Please select one publication and one subscription.")

if error_message:
  qs = '?portal_status_message=%s' % error_message
  return request.RESPONSE.redirect( context.absolute_url() + '/' + form_id + qs )


from DateTime import DateTime

callback = "SynchronizationTool_checkPointFixe"
active_process_path = site.portal_activities.newActiveProcess(start_date=DateTime(), causality_value=sub).getPath()
method_kw = {
  "publication_path" : pub.getPath(),
  "subscription_path" : sub.getPath(),
  "active_process" : active_process_path,
}
activate_kw = {
  "priority" : 3,
  "activity" : "SQLQueue",
}

# Register start of point fixe
from Products.CMFActivity.ActiveResult import ActiveResult
active_result = ActiveResult()
active_result.edit(summary='Info',
                   severity=0,
                   detail="Point fixe check launched at %r" % (DateTime().strftime("%d/%m/%Y %H:%M"),))
sub.activate(active_process=active_process_path,
            activity='SQLQueue',
            priority=2,).ERP5Site_saveCheckCatalogTableResult(active_result)

context.SynchronizationTool_activateCheckPointFixe(callback=callback, method_kw=method_kw, activate_kw=activate_kw)

qs = '?portal_status_message=%s' % "Point fixe running, active process path is %s" % (active_process_path,)
return request.RESPONSE.redirect( context.absolute_url() + '/' + form_id + qs )
