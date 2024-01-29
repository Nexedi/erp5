"""Produce an xml fragment for this accounting transaction and post it to the
active result.
We need a proxy role to post the result.
"""
import zlib
from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
active_process = portal.restrictedTraverse(active_process)
accounting_line_list = context.contentValues(portal_type=portal.getPortalAccountingMovementTypeList())

if context.getSourceSectionUid() in section_uid_list:
  if any([line.getSource(portal_type='Account') for line in accounting_line_list]):
    source_xml = context.AccountingTransaction_viewAsSourceFECXML(
      test_compta_demat_compatibility=test_compta_demat_compatibility)
    active_process.postResult(ActiveResult(detail=zlib.compress(source_xml.encode('utf8'))))

if context.getDestinationSectionUid() in section_uid_list:
  if any([line.getDestination(portal_type='Account') for line in accounting_line_list]):
    destination_xml = context.AccountingTransaction_viewAsDestinationFECXML(
      test_compta_demat_compatibility=test_compta_demat_compatibility)
    active_process.postResult(ActiveResult(detail=zlib.compress(destination_xml.encode('utf8'))))
