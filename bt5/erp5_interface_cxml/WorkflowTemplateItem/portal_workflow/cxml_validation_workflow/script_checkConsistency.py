doc = state_change['object']
doc.Base_checkConsistency()


version = getattr(doc, 'version', None)

if version:
  search_kw = {
     'portal_type' : doc.getPortalType(),
     'validation_state' : "validated",
  }
  portal_type = doc.getPortalType()
  if portal_type in ("Computing Cost Rate", "Extra Cost Factor", "Unfinished Work"):
    search_kw["title"] = doc.getTitle(),
  if portal_type == "Unfinished Work":
    ledger_uid = doc.getLedgerUid()
    if ledger_uid:
      search_kw['ledger_uid'] = ledger_uid
  previous_version_list = doc.getPortalObject().portal_catalog(**search_kw)

  for pdoc in previous_version_list:
    pdoc = pdoc.getObject()
    if pdoc.getPortalType() == "Internal Supply" and (pdoc.getStartDate() != doc.getStartDate() or \
      pdoc.getStopDate() != doc.getStopDate()):
      continue
    if float(version) < float(pdoc.getVersion()):
      from Products.DCWorkflow.DCWorkflow import ValidationFailed
      raise ValidationFailed(doc.Base_translateString('Impossible to validate document because higher version (${version}) already validated',
        mapping={"version": pdoc.getVersion()}))
