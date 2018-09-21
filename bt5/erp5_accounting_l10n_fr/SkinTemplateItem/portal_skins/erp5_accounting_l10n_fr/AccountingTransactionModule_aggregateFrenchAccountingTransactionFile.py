from cStringIO import StringIO
import zipfile
from Products.ERP5Type.Message import translateString

portal = context.getPortalObject()
active_process = portal.restrictedTraverse(active_process)

# XXX we need proxy role for this
result_list = [ result.detail.decode('zlib') for result in active_process.getResultList() ]
result_list.sort()

fec_file = context.AccountingTransactionModule_viewComptabiliteAsFECXML(
      at_date=at_date,
      result_list=result_list)

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
