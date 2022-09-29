sub_path = method_kw.get("subscription_path")
sub = context.getPortalObject().restrictedTraverse(sub_path)
search_kw = dict(kw)
packet_size = search_kw.pop('packet_size', 30)
limit = packet_size * search_kw.pop('activity_count', 100)

r = sub.getDocumentIdList(limit=limit, **search_kw)

result_count = len(r)
if result_count:
  if result_count == limit:
    # Recursive call to prevent too many activity generation
    next_kw = dict(activate_kw, priority=1+activate_kw.get('priority', 1))
    kw["min_id"] = r[-1].getId()
    sub.activate(**next_kw).SynchronizationTool_activateCheckPointFixe(
      callback, method_kw, activate_kw, **kw)

  r = [x.getId() for x in r]
  callback_method = getattr(sub.activate(**activate_kw), callback)
  for i in xrange(0, result_count, packet_size):
    callback_method(id_list=r[i:i+packet_size],
                    **method_kw)

if result_count < limit:
  # Register end of point fixe
  from Products.CMFActivity.ActiveResult import ActiveResult
  active_result = ActiveResult()
  active_result.edit(summary='Info',
                   severity=0,
                   detail="Point fixe check ended at %r" % (DateTime().strftime("%d/%m/%Y %H:%M"),))
  sub.activate(active_process=method_kw["active_process"],
              activity='SQLQueue',
              priority=2,).ERP5Site_saveCheckCatalogTableResult(active_result)
