import json

kw.update(context.REQUEST.form)

if not kw:
  return json.dumps(dict(response=False))

portal = context.getPortalObject()
person = portal.portal_catalog.getResultValue(portal_type="Person",
                                              validation_state="validated",
                                              ignore_unknown_columns=True,
                                              **kw)

return json.dumps(dict(response=(person is not None)))
