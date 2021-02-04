import textwrap
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript

class TestWebServiceTool(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return (
        'erp5_dms',
        'erp5_web_services',
    )

  def test_document_connector(self):
    doc = self.portal.document_module.newContent(
        portal_type='Spreadsheet',
        reference=self.id())
    doc.share()
    self.tic()
    createZODBPythonScript(
        self.portal.portal_skins.custom,
        'DocumentConnector_getDocumentUid',
        'reference',
        textwrap.dedent('''\
        assert reference == %s
        doc, = context.getPortalObject().portal_catalog.getDocumentValueList(reference=reference)
        return doc.getUid()
        ''' % repr(self.id()))
    )
    connection = self.portal.portal_web_services.connect(self.id(), transport='document')
    self.assertEqual(
        connection.getDocumentUid(),
        ('%s/DocumentConnector_getDocumentUid' % self.portal.getId(), doc.getUid()))
