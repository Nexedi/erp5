# coding: utf-8
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestIndexationBug(ERP5TypeTestCase):

  def _checkDocumentIsIndexed(self, document, indexed_category_expected_count):
    # Check that the catalog table contains the object
    sql_result = self.portal.portal_catalog.getResultValue(
      uid=document.getUid()
    )
    self.assertTrue(sql_result is not None, 'Document %s is not indexed' % document.getRelativeUrl())

    # Check that all categories are indexed
    category_tool = self.portal.portal_categories
    indexed_category_count = 0
    for category_relative_url in document.getCategoryList():
      # If the category object does not exist anymore
      # it should not be in the category table
      category = category_tool.restrictedTraverse(category_relative_url, default=None)
      if category is not None:
        indexed_category_count += 1
        search_dict = {}
        search_dict['%s__uid' % category_relative_url.split('/', 1)[0]] = category.getUid()
        sql_result = self.portal.portal_catalog.getResultValue(
          uid=document.getUid(),
          **search_dict
        )
        self.assertTrue(sql_result is not None, 'Category %s is not indexed on %s' % (category_relative_url, document.getRelativeUrl()))

    self.assertEquals(
      indexed_category_count,
      indexed_category_expected_count,
      'All document categories %s are not indexed (%i != %s)' % (document.getRelativeUrl(), indexed_category_count, indexed_category_expected_count)
    )

  def test_notIndexedDocumentBecauseOfBrokenFallbackCategoryAcquisition(self):
    """
    When a category uses the fallback_category acquisition,
    it can lead to a wrong indexation if the category value does not exist
    Example: time_quantity_unit acquires quantity_unit
    """
    # First, check empty object
    product = self.portal.product_module.newContent(
      portal_type='Product'
    )
    sale_supply = self.portal.sale_supply_module.newContent(
      portal_type='Sale Supply'
    )
    supply_line = sale_supply.newContent(
      portal_type='Sale Supply Line'
    )
    supply_cell = supply_line.newContent(
      portal_type='Sale Supply Cell'
    )
    self.tic()
    self._checkDocumentIsIndexed(supply_line, 0)

    # Then, set some existing categories
    supply_cell.edit(
      # This category exist
      # Strictly speaking, we never set the resource on the cell
      # but it is enough to reproduce the bug
      resource_value=product
    )
    self.tic()
    self._checkDocumentIsIndexed(supply_cell, 1)

    # Set a non existing acquired category on parent
    supply_line.edit(
      quantity_unit='notexistingfoobarquantityunit'
    )
    self.tic()
    self._checkDocumentIsIndexed(supply_cell, 1)

