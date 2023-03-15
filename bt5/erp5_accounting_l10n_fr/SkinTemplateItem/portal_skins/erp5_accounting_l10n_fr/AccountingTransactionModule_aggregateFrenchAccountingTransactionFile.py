# coding: utf-8
import unicodedata
import six
from io import BytesIO
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
  # normalize all non ascii characters (é => e), while still keeping
  # some "important" characters such as €
  # https://github.com/DGFiP/Test-Compta-Demat/issues/37
  # https://github.com/DGFiP/Test-Compta-Demat/issues/39
  fec_file = unicodedata.normalize(
    'NFKD', fec_file.replace(u"€", "EUR")
  ).encode('ascii', 'ignore')

zipbuffer = BytesIO()
zipfilename = at_date.strftime('FEC-%Y%m%d.zip')
zipfileobj = zipfile.ZipFile(zipbuffer, 'w', compression=zipfile.ZIP_DEFLATED)
filename = 'FEC.xml'
if test_compta_demat_compatibility:
  siren = ''
  if section_uid_list:
    siret_list = [b.getObject().getCorporateRegistrationCode() for b in portal.portal_catalog(uid=section_uid_list)]
    siret_list = [siret for siret in siret_list if siret]
    if len(siret_list) == 1:
      siren = siret_list[0][:8]
  filename = at_date.strftime('{siren}FEC%Y%m%d.xml').format(siren=siren)
zipfileobj.writestr(filename, fec_file.encode('utf8'))
zipfileobj.close()

attachment_list = (
    {'mime_type': 'application/zip',
     'content': zipbuffer.getvalue(),
     'name': zipfilename, }, )

subject = translateString('French Accounting Transaction File')
if six.PY2:
  subject = unicode(subject)
else:
  subject = str(subject)

portal.ERP5Site_notifyReportComplete(
    user_name=user_name,
    subject=subject,
    message='',
    attachment_list=attachment_list)

# delete no longer needed active process
active_process.getParentValue().manage_delObjects(ids=[active_process.getId()])
