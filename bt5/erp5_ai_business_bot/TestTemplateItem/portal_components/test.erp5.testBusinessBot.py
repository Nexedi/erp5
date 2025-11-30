from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class Test(ERP5TypeTestCase):
  """
  A test class to test the Business Bot module
  """

  def getTitle(self):
    return "TestBusinessBot"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base', 'erp5_web', 'erp5_ingestion_mysql_innodb_catalog', 'erp5_crm', 'erp5_dms', 'erp5_business_bot')

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    message_list = [
      dict(title='Tagged Message', subject_list=['ERP5', 'pricing'], text_content="ERP5 pricing"),
      dict(title='Untagged Message', subject_list=[], text_content="ERP5 pricing"),
    ]
    for index, message in enumerate(message_list):
      kw = dict(portal_type = 'Web Message', title = message_list[index]["title"], subject = message_list[index]["subject_list"])
      existing = self.portal.portal_catalog.getResultValue(**kw)
      if existing is None:
        self.portal.event_module.newContent(**kw)

    self.commit()
    self.tic()

  def test_setWebMessageModel(self):
    """
    Use case: user has one or more tagged messages
    and wants to train a model on them.  This model now
    exists in the document module.
    """

    set_model_result = self.portal.event_module.WebMessage_setModel().split()
    self.assertEqual(set_model_result[0], "Model")
    kw = dict(portal_type = 'File', title = "AI Business Bot")
    document = self.portal.portal_catalog.getResultValue(**kw)
    self.assertEqual(set_model_result[3], "/erp5/" + document.getRelativeUrl())

  def test_testWebMessageModel(self):
    """
    Use case: user wants to know how accurate the model
    would be given the current algorithm for the model and
    the current tagged messages.  Data is returned to user.
    """
    self.assertEqual(self.portal.event_module.WebMessage_testModel().split()[0] , "Model")

  def test_followUpAutomatically(self):
    """
    Use case: user has an untagged message that they 
    wish would be handled by the model.  This message now
    has tags.
    """
    self.portal.event_module.WebMessage_setModel()
    kw = dict(portal_type = 'Web Message', title='Untagged Message')
    message = self.portal.portal_catalog.getResultValue(**kw)
    message.WebMessage_parseWebMessage()
    self.assertFalse(message.getSubjectList() == "[]")