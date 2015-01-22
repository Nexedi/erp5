import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
#from Acquisition import aq_inner
#from Acquisition import aq_parent
class TestERP5Workflow(ERP5TypeTestCase):
  """
    Tests ERP5 Workflow.
  """

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_workflow',)

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.workflow_module = self.portal.workflow_module
    self.login() # as Manager

  def test01_Erp5AccessorMethod(self):
    """Generate Transition Methods and test these methods."""
    # Create base category as the intermidiate
    self.portal.portal_categories.newContent('new_state')

    # Create a workflow
    new_workflow = self.workflow_module.newContent(portal_type='Workflow',
                                                   id='new_workflow')
    s1 = new_workflow.newContent(portal_type='State',title='Draft', id='draft')
    s2 = new_workflow.newContent(portal_type='State',title='Validated', id='validated')
    s3 = new_workflow.newContent(portal_type='State',title='Couscous', id='Couscous')

    #raise NotImplementedError(aq_parent(aq_inner(aq_parent(aq_inner(s1)))))### <Workflow Module at workflow_module>
    #raise NotImplementedError(aq_inner(aq_parent(aq_inner(s1))))### <Workflow at new_workflow>
    #raise NotImplementedError(aq_parent(aq_inner(s1)))### <Workflow at new_workflow>
    #raise NotImplementedError(aq_inner(s1))### <State at draft>
    #raise NotImplementedError(s1)### <State at draft>
    t1 = new_workflow.newContent(
      portal_type='Transition',
      title='Transition 1',
      id='transition1')
    t2 = new_workflow.newContent(
      portal_type='Transition',
      title='Transition 2',
      id='transition2')
    t3 = new_workflow.newContent(
      portal_type='Transition',
      title='Transition 3',
      id='set_to_couscous_please')
    s1.setDestinationValueList([t1, t3])
    s2.setDestinationValueList([t2, t3])
    t1.setDestinationValue(s2)
    t2.setDestinationValue(s1)
    t3.setDestinationValue(s3)
    
    #raise NotImplementedError (s2.getDestinationValueList()) 
    # set initial state
    new_workflow.setSourceValue(s1)

    # state variable
    new_workflow.setStateBaseCategory('new_state',)

    # create a base type and a portal type based on this base type
    type_object = self.portal.portal_types.newContent(
      portal_type='Base Type',
      id='Object Type',
      type_class='XMLObject',
      type_base_category_list=(['new_state',])
      )

    type_object.edit(type_erp5workflow_list=('new_workflow',))
    #type_object.erp5workflow_list = ('new_workflow',)
    # create a module
    self.portal.portal_types.newContent(
      'Module Type', 'Base Type',
      type_class='Folder',
      type_filter_content_type=1,
      type_allowed_content_type_list=('Object Type',))

    self.portal.newContent(portal_type='Module Type', id='new_module')

    # create an object based on new-created portal type in the module
    new_object = self.portal.new_module.newContent(portal_type='Object Type',
                                                    id='new_object')

    self.assertTrue(new_object is not None)
    self.assertEqual(new_object.getPortalType(), 'Object Type')

    self.portal.Localizer._default_language = 'fr' # switch language
    message_catalog = self.portal.Localizer.erp5_ui
    message_catalog.message_edit('Draft', 'fr', 'Brouillon', '')

    self.assertEqual(new_object.getNewState(), 'draft')
    self.assertEqual(new_object.getNewStateTitle(), 'Draft')
    self.assertEqual(new_object.getTranslatedNewStateTitle(), 'Brouillon')

    ### execute transition
    t1.execute(new_object)
    self.assertEqual(new_object.getNewStateTitle(), 'Validated')


    ### call accessor
    new_object.transition2()
    self.assertEqual(new_object.getNewStateTitle(), 'Draft')

    new_object.transition1()
    self.assertEqual(new_object.getNewStateTitle(), 'Validated')

    new_object.setToCouscousPlease()
    self.assertEqual(new_object.getNewStateTitle(), 'Couscous')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  return suite