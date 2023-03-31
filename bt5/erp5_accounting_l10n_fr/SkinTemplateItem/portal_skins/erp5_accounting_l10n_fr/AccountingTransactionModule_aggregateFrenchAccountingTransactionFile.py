# coding: utf-8
from cStringIO import StringIO
import zipfile
from Products.ERP5Type.Message import translateString

portal = context.getPortalObject()
active_process = portal.restrictedTraverse(active_process)

# XXX we need proxy role for this
result_list = active_process.getResultList()

fec_file = context.AccountingTransactionModule_viewComptabiliteAsFECXML(
      at_date=at_date,
      result_list=result_list)
if test_compta_demat_compatibility:
  fec_file = (fec_file
    # https://github.com/DGFiP/Test-Compta-Demat/issues/37
    .replace(u"’", u"'")
    .replace(u"Œ", u"OE")
    .replace(u"œ", u"oe")
    .replace(u"Ÿ", u"Y")
    # https://github.com/DGFiP/Test-Compta-Demat/issues/39
    .replace(u"€", u"EUR")
)

zipbuffer = StringIO()
zipfilename = at_date.strftime('FEC-%Y%m%d.zip')
zipfileobj = zipfile.ZipFile(zipbuffer, 'w', compression=zipfile.ZIP_DEFLATED)
zipfileobj.writestr('FEC.xml', fec_file.encode('utf8'))
zipfileobj.close()

attachment_list = (
    {'mime_type': 'application/zip',
     'content': zipbuffer.getvalue(),
     'name': zipfilename, }, )

portal.ERP5Site_notifyReportComplete(
    user_name=user_name,
    subject=unicode(translateString('French Accounting Transaction File')),
    message='',
    attachment_list=attachment_list)

# delete no longer needed active process
active_process.getParentValue().manage_delObjects(ids=[active_process.getId()])
