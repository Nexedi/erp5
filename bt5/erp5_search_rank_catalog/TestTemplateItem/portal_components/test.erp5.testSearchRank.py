# -*- coding: utf-8 -*-
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from decimal import Decimal

def wipeFolder(folder, commit=True):
  folder.deleteContent(list(folder.objectIds()))
  if commit:
    transaction.commit()

class TestSearchRank(ERP5TypeTestCase):
  def afterSetUp(self):
    self.login()
    wipeFolder(self.portal.foo_module, commit=False)

  def beforeTearDown(self):
    transaction.abort()

  def generateNewId(self):
    return "%sö" % self.portal.portal_ids.generateNewId(
                                     id_group=('erp5_search_rank_test'))

  def _makeDocument(self):
    new_id = self.generateNewId()
    foo = self.portal.foo_module.newContent(portal_type="Foo")
    foo.edit(
      title="live_test_%s" % new_id,
      reference="live_test_%s" % new_id
    )
    return foo

  def assertIndexedDocumentSearchRankEqual(self, document, string_rank):
    sql_result_list = self.portal.portal_catalog(
      uid=document.getUid(),
      select_list=['search_rank'],
      limit=1
    )
    self.assertEqual(
      sql_result_list[0].search_rank,
      Decimal(string_rank)
    )

  def test_rank_value(self):
    # Newly created document without rank calculated yet
    document = self._makeDocument()
    self.tic()
    self.assertIndexedDocumentSearchRankEqual(document, '0')

    # reindexation does not recalculate the search rank
    document.reindexObject()
    self.tic()
    self.assertIndexedDocumentSearchRankEqual(document, '0')

    # calculate search rank for document without any (related) relation
    document.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '15000')

    # search rank calculation is stable
    document.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '15000')

    # reindexation does not modify the search rank
    document.reindexObject()
    self.tic()
    self.assertIndexedDocumentSearchRankEqual(document, '15000')

    # Create document to link to
    linked_document_1 = self._makeDocument()
    linked_document_2 = self._makeDocument()
    self.tic()
    linked_document_1.Base_updateSearchRank()
    linked_document_2.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '15000')

    # Linked from one document only
    linked_document_1.setFooCategoryValue(document)
    self.tic()
    document.Base_updateSearchRank()
    linked_document_1.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '27750')
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '15000')

    # Linked from one document only with no score
    linked_document_1.setFooCategoryValue(document)
    linked_document_1.Base_zUpdateSearchRank(
      uid=linked_document_1.getUid(),
      search_rank=0
    )
    self.tic()
    document.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '0')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '15000')

    # Linked from one document only with a lower score
    linked_document_1.setFooCategoryValue(document)
    linked_document_1.Base_zUpdateSearchRank(
      uid=linked_document_1.getUid(),
      search_rank=100
    )
    self.tic()
    document.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '15085')
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '100')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '15000')

    # Linked from 2 documents (rank is higher than one doc only)
    linked_document_1.setFooCategoryValue(document)
    linked_document_2.setFooCategoryValue(document)
    self.tic()
    linked_document_1.Base_updateSearchRank()
    linked_document_2.Base_updateSearchRank()
    document.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '40500')
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '15000')

    # reset ranks
    linked_document_1.setFooCategoryValue(None)
    linked_document_2.setFooCategoryValue(None)
    self.tic()
    document.Base_updateSearchRank()
    linked_document_1.Base_updateSearchRank()
    linked_document_2.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '15000')

    # Linked from 1 document with a higher rank
    linked_document_1.setFooCategoryValue(document)
    linked_document_2.setFooCategoryValue(linked_document_1)
    self.tic()
    linked_document_2.Base_updateSearchRank()
    linked_document_1.Base_updateSearchRank()
    document.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '38587')
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '27750')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '15000')

    # reset ranks
    linked_document_1.setFooCategoryValue(None)
    linked_document_2.setFooCategoryValue(None)
    self.tic()
    document.Base_updateSearchRank()
    linked_document_1.Base_updateSearchRank()
    linked_document_2.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '15000')

    # Linked from 1 document with many categories
    linked_document_1.setFooCategoryValueList([document, linked_document_2])
    self.tic()
    linked_document_2.Base_updateSearchRank()
    linked_document_1.Base_updateSearchRank()
    document.Base_updateSearchRank()
    self.assertIndexedDocumentSearchRankEqual(document, '21375')
    self.assertIndexedDocumentSearchRankEqual(linked_document_1, '15000')
    self.assertIndexedDocumentSearchRankEqual(linked_document_2, '21375')
