import unittest
from erp5.component.test.testInventory import TestInventory


class TestInventoryWithStockCache(TestInventory):
  "Test Inventory API with erp5_stock_cache"

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInventoryWithStockCache))
  return suite
