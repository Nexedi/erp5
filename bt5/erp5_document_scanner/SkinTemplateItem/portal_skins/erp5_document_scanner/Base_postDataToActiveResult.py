"""
  We need proy role as manager to create a new active process
  and post active result
"""
import string
import random

portal = context.getPortalObject()

if REQUEST:
  return RuntimeError("You cannot run this script in the url")

reference = context.Base_getDocumentScannerDefaultReference()
if active_process_url:
  active_process = portal.restrictedTraverse(active_process_url)
else:
  active_process = portal.portal_activities.newActiveProcess(
    reference=reference)

if generate_new_uid:
  new_uid = len(list(active_process.getResultList()))
else:
  new_uid = None

active_process.postActiveResult(detail=detail, reference=new_uid)
return active_process, new_uid
