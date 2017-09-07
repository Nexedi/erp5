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

  message_reference_dict = {}
  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    message_list = [
      dict(title='Tagged Message', subject_list=['ERP5', 'pricing'], text_content="ERP5 pricing"),
      dict(title='Untagged Message', text_content="ERP5 pricing"),
    ]
    for message in message_list:
      kw = dict(portal_type = 'Web Message', title = message_list[title], text_content=message_list[text_content])
      existing = self.portal_catalog.getResultValue(**kw)
      if existing is None:
        self.message_reference_dict[message['reference']] = self.event_module.newContent(**kw).getReference()
      else:
        self.message_reference_dict[message['reference']] = existing.getReference()

    self.commit()
    self.tic()

  def test_setWebMessageModel(self):
    """
    Use case: user has one or more tagged messages
    and wants to train a model on them.  This model now
    exists in the document module.
    """

    set_model_result = self.event_module.set_model().split()
    self.assertEqual(set_model_result[0], "Model")
    kw = dict(portal_type = 'Document', title = "AI Business Bot")
    document = self.portal_catalog.getResultValue(**kw)
    self.assertEqual(set_model_result[3], document.getRelativeUrl())

  def test_testWebMessageModel(self):
    """
    Use case: user wants to know how accurate the model
    would be given the current algorithm for the model and
    the current tagged messages.  Data is returned to user.
    """
    self.assertEqual(self.event_module.test_model().split()[0] , "Model")

  def test_followUpAutomatically(self):
    """
    Use case: user has an untagged message that they 
    wish would be handled by the model.  This message now
    has tags.
    """
    self.event_module.set_model()
    kw = dict(portal_type = 'Web Message', title='Untagged Message', text_content="ERP5 pricing")
    message = self.portal_catalog.getResultValue(**kw)
    message.follow_up_automatically()
    self.assertEqual(message.getSubjectList(), ['ERP5', 'pricing'])
