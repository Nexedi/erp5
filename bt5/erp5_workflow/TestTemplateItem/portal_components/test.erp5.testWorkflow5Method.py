import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

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

  def test_Erp5TransitionMethod(self):
    """Generate Transition Methods and test these methods."""
    # Create base category as the intermidiate
    self.portal.portal_categories.newContent('category_state')

    # Create a workflow
    new_workflow = self.workflow_module.newContent(portal_type='Workflow',
                                                   id='new_workflow')
    s1 = new_workflow.newContent(portal_type='State',title='draft')
    s2 = new_workflow.newContent(portal_type='State',title='validated')
    s3 = new_workflow.newContent(portal_type='State',title='couscous')

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
    new_workflow.setStateBaseCategory('category_state',)

    # create a base type and a portal type based on this base type
    type_object = self.portal.portal_types.newContent(
      portal_type='Base Type',
      id='Object Type',
      type_class='XMLObject',
      type_base_category_list=(['category_state',])
      )

    type_object.setWorkflow5Value(new_workflow)
    type_object.workflow_list=('new_workflow',)
    #type_object.setProperty('Transition_2', new_workflow)

    self.assertEqual(type_object.getBaseCategoryList(), ['workflow5'])
    self.assertEqual(type_object.getWorkflow5(),
      'workflow_module/new_workflow')
    self.assertEqual(len(type_object.getWorkflow5ValueList()), 1)

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
    self.assertEqual(new_object.getCategoryStateTitle(), 'draft')

    ### execute transition
    t1.execute(new_object)
    #new_object.transition1()
    self.assertEqual(new_object.getCategoryStateTitle(), 'validated')

    ### call accessor
    #new_object.quoi() # accessor is not whatever
    new_object.transition2()
    #from thread import get_ident
    #raise NotImplementedError (get_ident())
    #raise NotImplementedError (new_object.transition2().__class__)# <type 'NoneType'>
    self.assertEqual(new_object.getCategoryStateTitle(), 'draft')

    new_object.transition1()
    self.assertEqual(new_object.getCategoryStateTitle(), 'validated')


    #new_object.set_to_couscous_please()
    new_object.setToCouscousPlease()
    self.assertEqual(new_object.getCategoryStateTitle(), 'couscous')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  return suite