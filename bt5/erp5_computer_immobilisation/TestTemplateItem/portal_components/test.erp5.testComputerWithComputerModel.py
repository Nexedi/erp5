# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestComputerWithComputerModel(ERP5TypeTestCase):
  def afterSetUp(self):
    pass

  def beforeTearDown(self):
    pass

  def newModel(self, **kw):
    return self.portal.computer_model_module.newContent(
      portal_type='Computer Model', **kw)

  def newComputer(self, **kw):
    return self.portal.computer_module.newContent(
      portal_type='Computer', **kw)

  def test_apply_model_empty_computer(self):
    category_list = ['mana', 'mahna']
    model = self.newModel(group=category_list)
    computer = self.newComputer(specialise_value=model)
    self.assertEqual(computer.getPropertyList('group'), [])
    result = computer.Computer_applyComputerModel()
    self.assertEqual(computer.getPropertyList('group'), category_list)
    self.assertTrue('=Computer%20Model%20applied.' in result, result)

  def test_apply_model_empty_computer_batch_mode(self):
    category_list = ['mana', 'mahna']
    model = self.newModel(group=category_list)
    computer = self.newComputer(specialise_value=model)
    self.assertEqual(computer.getPropertyList('group'), [])
    result = computer.Computer_applyComputerModel(batch_mode=1)
    self.assertEqual(computer.getPropertyList('group'), category_list)
    self.assertTrue(result)

  def test_apply_model_filled_computer(self):
    computer_category_list = ['oink']
    category_list = ['mana', 'mahna']
    model = self.newModel(group=category_list)
    computer = self.newComputer(specialise_value=model,
      group=computer_category_list)
    self.assertEqual(computer.getPropertyList('group'),
      computer_category_list)
    result = computer.Computer_applyComputerModel()
    self.assertEqual(computer.getPropertyList('group'),
      computer_category_list)
    self.assertTrue('=No%20changes%20applied.' in result, result)

  def test_apply_model_filled_computer_batch_mode(self):
    computer_category_list = ['oink']
    category_list = ['mana', 'mahna']
    model = self.newModel(group=category_list)
    computer = self.newComputer(specialise_value=model,
      group=computer_category_list)
    self.assertEqual(computer.getPropertyList('group'),
      computer_category_list)
    result = computer.Computer_applyComputerModel()
    self.assertEqual(computer.getPropertyList('group'),
      computer_category_list)
    self.assertTrue(result)

  def test_apply_model_filled_computer_forced(self):
    computer_category_list = ['oink']
    category_list = ['mana', 'mahna']
    model = self.newModel(group=category_list)
    computer = self.newComputer(specialise_value=model,
      group=computer_category_list)
    self.assertEqual(computer.getPropertyList('group'),
      computer_category_list)
    result = computer.Computer_applyComputerModel(force=1)
    self.assertEqual(computer.getPropertyList('group'),
      category_list)
    self.assertTrue('=Computer%20Model%20applied.' in result, result)

  def test_apply_model_filled_computer_force_batch_mode(self):
    computer_category_list = ['oink']
    category_list = ['mana', 'mahna']
    model = self.newModel(group=category_list)
    computer = self.newComputer(specialise_value=model,
      group=computer_category_list)
    self.assertEqual(computer.getPropertyList('group'),
      computer_category_list)
    result = computer.Computer_applyComputerModel(force=1, batch_mode=1)
    self.assertEqual(computer.getPropertyList('group'),
      category_list)
    self.assertTrue(result)

  def test_apply_no_model(self):
    computer = self.newComputer()
    result = computer.Computer_applyComputerModel()
    self.assertTrue('=No%20Computer%20Model.' in result, result)

  def test_apply_no_model_batch_mode(self):
    computer = self.newComputer()
    result = computer.Computer_applyComputerModel(batch_mode=1)
    self.assertEqual(False, result)

  def test_category_coverage(self):
    category_dict = {
      'cpu_core': ['cpu_core1', 'cpu_core2'],
      'cpu_frequency': ['cpu_frequency1', 'cpu_frequency2'],
      'cpu_type': ['cpu_type1', 'cpu_type2'],
      'function': ['function1', 'function2'],
      'group': ['group1', 'group2'],
      'local_area_network_type': ['local_area_network_type1',
        'local_area_network_type2'],
      'memory_size': ['memory_size1', 'memory_size2'],
      'memory_type': ['memory_type1', 'memory_type2'],
      'region': ['region1', 'region2'],
      'storage_capacity': ['storage_capacity1', 'storage_capacity2'],
      'storage_interface': ['storage_interface1', 'storage_interface2'],
      'storage_redundancy': ['storage_redundancy1', 'storage_redundancy2'],
    }
    model = self.newModel(**category_dict)

    category_list = []
    for k, v in category_dict.iteritems():
      for l in v:
        category_list.append('%s/%s' % (k,l))
    category_list.append('specialise/%s' % model.getRelativeUrl())
    computer = self.newComputer(specialise_value=model)
    result = computer.Computer_applyComputerModel()
    self.assertSameSet(category_list, computer.getCategoryList())
    self.assertTrue('=Computer%20Model%20applied.', result)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestComputerWithComputerModel))
  return suite
