"""
  We need proy role as manager to create a new active process
  and post active result
"""
import string
import random

portal = context.getPortalObject()

if REQUEST:
  return RuntimeError("You cannot run this script in the url")

if active_process_url:
  active_process = portal.restrictedTraverse(active_process_url)
else:
  active_process = portal.portal_activities.newActiveProcess()
  active_process.setReference("document_scanner_js")

if generate_new_uid:
  id_group = ('document_scanner_js', active_process.getUid())
  new_uid = portal.portal_ids.generateNewId(id_group=id_group, default=0)
else:
  new_uid = None

active_process.postActiveResult(detail=detail, reference=new_uid)
return active_process, new_uid
