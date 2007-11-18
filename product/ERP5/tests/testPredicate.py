#############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

"""
  Tests Predicates

"""

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList

REGION_FRANCE_PATH = 'region/europe/western_europe/france'
REGION_GERMANY_PATH = 'region/europe/western_europe/germany'
GROUP_STOREVER_PATH = 'group/nexedi/storever'
GROUP_OTHER_PATH = 'group/other'

RUN_ALL_TESTS = 1
QUIET = 1
PREDICATE_FOLDER_NAME = "predicate_unit_test_folder"

class TestPredicates(ERP5TypeTestCase):
  """Test Predicates. """
  
  def getTitle(self):
    return "Predicates"
  
  def login(self) :
    """sets the security manager"""
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Member', 'Assignee', 'Assignor',
                               'Auditor', 'Author', 'Manager'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)
  
  def afterSetUp(self) :
    self.createCategories()
    self.login()
    
  # XXX ... this method is a copy / paste
  def playSequence(self, sequence_string, quiet=QUIET) :
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=QUIET)
  
  # XXX ... this method is a copy / paste
  def createCategories(self):
    """Create the list of categories returned by the
    `getNeededCategoryList` Method.
    """
    # create categories
    for cat_string in self.getNeededCategoryList() :
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in path.objectIds() :
          path = path.newContent(
            portal_type = 'Category',
            id = cat,
            immediate_reindex = 1 )
        else :
          path = path[cat]

    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ( REGION_FRANCE_PATH, REGION_GERMANY_PATH,
             GROUP_STOREVER_PATH, GROUP_OTHER_PATH )
  
  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', )
  
  def getPredicateFolder(self):
    """Return a folder for predicates."""
    if PREDICATE_FOLDER_NAME in self.getPortal().objectIds() :
      predicate_folder = self.getPortal()[PREDICATE_FOLDER_NAME]
    else :
      predicate_folder = self.getPortal().newContent(
                                        portal_type = 'Folder',
                                        id = PREDICATE_FOLDER_NAME)
    self.failUnless('Predicate' in [x.id for x in
                    predicate_folder.allowedContentTypes()])
    return predicate_folder

  def createPredicate(self, **kw):
    """Generic method to create a predicate"""
    return self.getPredicateFolder().newContent(
                        portal_type = 'Predicate', **kw)
  
  def createDocument(self, **kw):
    """Creates a document."""
    return self.getOrganisationModule().newContent(
                             portal_type='Organisation', **kw)
    
  def stepCreatePredicateTrueScript(self, sequence=None, **kw) :
    """Creates a script that always return true"""
    createZODBPythonScript(self.getPortal().portal_skins.erp5_base,
                           'Predicate_true', 'predicate', """return 1""")
    sequence.edit(test_method_id = 'Predicate_true')
  
  def stepCreatePredicateFalseScript(self, sequence=None, **kw) :
    """Creates a script that always return false"""
    createZODBPythonScript(self.getPortal().portal_skins.erp5_base,
                           'Predicate_false', '', """return 0""")
    sequence.edit(test_method_id = 'Predicate_false')
    
  def stepCreateTestMethodIdPredicate(self, sequence=None, **kw) :
    """Creates a predicate with a test method_id"""
    sequence.edit(predicate = self.createPredicate(
        test_method_id = sequence.get('test_method_id')))
  
  def stepCreateEmptyPredicate(self, sequence=None, **kw) :
    """Creates an empty predicate that is supposed to be always true"""
    sequence.edit(predicate = self.createPredicate())
  
  def stepCreateAlwaysFalsePredicate(self, sequence=None, **kw) :
    """Creates a predicate that is always false (membership of an non
       existant category)"""
    sequence.edit(predicate = self.createPredicate(
        membership_criterion_base_category_list = ['not_exist'],
        membership_criterion_category_list = ['not_exist/nothing']
      ))
  
  def stepCreateRegionFrancePredicate(self, sequence=None, **kw) :
    """Creates a predicate for region france category"""
    sequence.edit(predicate = self.createPredicate(
        membership_criterion_base_category_list = ['region'],
        membership_criterion_category_list = [REGION_FRANCE_PATH]
      ))
  
  def stepCreateRegionFranceTestMethodIdPredicate(
                                  self, sequence=None, **kw) :
    """Creates an region france predicate with the last test_method_id
    in the sequence"""
    sequence.edit(predicate = self.createPredicate(
        membership_criterion_base_category_list = ['region'],
        membership_criterion_category_list = [REGION_FRANCE_PATH],
        test_method_id = sequence.get('test_method_id')))
  
  
  def stepCreateGroupStoreverPredicate(self, sequence=None, **kw) :
    """Creates a predicate for group storever category"""
    sequence.edit(predicate = self.createPredicate(
        membership_criterion_base_category_list = ['group'],
        membership_criterion_category_list = [GROUP_STOREVER_PATH]
      ))
  
  def stepCreateGroupStoreverRegionFrancePredicate(
                                      self, sequence=None, **kw) :
    """Creates a predicate for group storever and region france
    categories"""
    sequence.edit(predicate = self.createPredicate(
        membership_criterion_base_category_list = ['group', 'region'],
        membership_criterion_category_list = [ GROUP_STOREVER_PATH,
                                               REGION_FRANCE_PATH ]
      ))
  
  def stepCreateRegionFrancePredicateTruePredicate(
                                      self, sequence=None, **kw) :
    """Creates a predicate for region france and Predicate_true script.
    """
    self.stepCreatePredicateTrueScript(sequence = sequence)
    sequence.edit(predicate = self.createPredicate(
        membership_criterion_base_category_list = ['region'],
        membership_criterion_category_list = [ REGION_FRANCE_PATH ],
        test_method_id = sequence.get('test_method_id')
      ))
                        
  def stepCreateRegionFrancePredicateFalsePredicate(
                                          self, sequence=None, **kw) :
    """Creates a predicate for region france and Predicate_false script.
    """
    self.stepCreatePredicateFalseScript(sequence = sequence)
    sequence.edit(predicate = self.createPredicate(
        membership_criterion_base_category_list = ['region'],
        membership_criterion_category_list = [ REGION_FRANCE_PATH ],
        test_method_id = sequence.get('test_method_id')
      ))
  
  def stepSaveFirstPredicate(self, sequence=None, **kw) :
    """Save current predicate for later fusion."""
    sequence.edit(first_predicate = sequence.get('predicate'))
    
  def stepMergePredicates(self, sequence=None, **kw) :
    """Merge `first predicate` with current predicate."""
    first_predicate = sequence.get('first_predicate')
    current_predicate = sequence.get('predicate')
    first_predicate.setPredicateCategoryList(
        [ first_predicate.getRelativeUrl(),
          current_predicate.getRelativeUrl() ])
    sequence.edit(predicate = first_predicate)
    
  def stepCreateDocument(self, sequence=None, **kw) :
    """Creates a document."""
    doc = self.getOrganisationModule().newContent(
                                      portal_type='Organisation')
    sequence.edit(doc = doc)
  
  def stepSetDocumentStoreverGroupMembership(
                                self, sequence=None, **kw) :
    """Set group membership for the document."""
    doc = sequence.get('doc')
    doc.setGroup(GROUP_STOREVER_PATH.replace('group/', ''))
  
  def stepSetDocumentOtherGroupMembership(self, sequence=None, **kw) :
    """Set group membership for the document."""
    doc = sequence.get('doc')
    doc.setGroup(GROUP_OTHER_PATH.replace('group/', ''))
                          
  def stepSetDocumentGermanyRegionMembership(self, sequence=None, **kw) :
    """Set region membership for the document."""
    doc = sequence.get('doc')
    doc.setRegion(REGION_GERMANY_PATH.replace('region/', ''))
  
  def stepSetDocumentFranceRegionMembership(self, sequence=None, **kw) :
    """Set region membership for the document."""
    doc = sequence.get('doc')
    doc.setRegion(REGION_FRANCE_PATH.replace('region/', ''))
  
  def stepAssertPredicateTrue(self, sequence=None, **kw) :
    """Assert the predicate is true on the document."""
    doc = sequence.get('doc')
    predicate = sequence.get('predicate')
    self.failUnless(predicate.test(doc))
  
  def stepAssertPredicateFalse(self, sequence=None, **kw) :
    """Assert the predicate is false on the document."""
    doc = sequence.get('doc')
    predicate = sequence.get('predicate')
    self.assertFalse(predicate.test(doc))

  ############################################################################
  ## Test Methods ############################################################
  ############################################################################
  
  def test_Interface(self):
    """Test Predicate implements Predicate interface."""
    from Products.ERP5Type.Interface import Predicate as IPredicate
    from Products.ERP5Type.Document.Predicate import Predicate
    predicate = self.createPredicate()
    self.failUnless(IPredicate.isImplementedBy(predicate))
    from Interface.Verify import verifyClass
    verifyClass(IPredicate, Predicate)


  def test_BasicCategoryMembership(self):
    # Predicates can test that a document is member of a category
    doc = self.createDocument(region='europe/western_europe/france',)
    pred = self.createPredicate(
        membership_criterion_base_category_list=['region'],
        membership_criterion_category_list=
                      ['region/europe/western_europe/france'])
    # our document is member of france region, so the predicate is true
    self.assertTrue(pred.test(doc))


  def test_BasicCategoryMembershipNotStrict(self):
    # Predicates are not only true for strict membership, but can also be used
    # with a parent category
    doc = self.createDocument(region='europe/western_europe/france',)
    pred = self.createPredicate(
        membership_criterion_base_category_list=['region'],
        membership_criterion_category_list=['region/europe'])
    self.assertTrue(pred.test(doc))


  def test_BasicCategoryNonMembership(self):
    # if the document is not member of the category, the predicate returns
    # false
    doc = self.createDocument(region='europe/western_europe/france',)
    pred = self.createPredicate(
        membership_criterion_base_category_list=['region'],
        membership_criterion_category_list=
                ['region/europe/western_europe/germany'])
    self.assertFalse(pred.test(doc))


  def test_NonExistantCategoryMembership(self):
    # the predicate also return false for non existant category and no error is
    # raised.
    doc = self.createDocument()
    pred = self.createPredicate(
        membership_criterion_base_category_list=['not_exist'],
        membership_criterion_category_list=['not_exist/nothing'])
    self.assertFalse(pred.test(doc))


  def test_EmptyPredicates(self):
    # empty predicate are true
    doc = self.createDocument()
    pred = self.createPredicate()
    self.assertTrue(pred.test(doc))


  def test_TestMethodId(self):
    doc = self.createDocument(region='europe/western_europe/france',)
    calls = []
    def true_method(predicate):
      calls.append(True)
      return True
    doc.true_method = true_method
    def false_method(predicate):
      calls.append(False)
      return False
    doc.false_method = false_method
    
    # predicates can also be created with a test method id, which will be the
    # id of a method to call on the document (of course it can be a python
    # script). This method must return a boolean value.
    pred = self.createPredicate(test_method_id='true_method')
    self.assertTrue(pred.test(doc))
    self.assertEquals([True], calls)

    pred = self.createPredicate(test_method_id='false_method')
    self.assertFalse(pred.test(doc))
    self.assertEquals([True, False], calls)
  
    # the use of method id can be mixed with category membership, both will
    # have to be true for the predicate to be true.
    pred = self.createPredicate(
        test_method_id='true_method',
        membership_criterion_base_category_list=['region'],
        membership_criterion_category_list=
                      ['region/europe/western_europe/france'])
    self.assertTrue(pred.test(doc))
    self.assertEquals([True, False, True], calls)
    
    pred = self.createPredicate(
        test_method_id='false_method',
        membership_criterion_base_category_list=['region'],
        membership_criterion_category_list=
                      ['region/europe/western_europe/france'])
    self.assertFalse(pred.test(doc))
    self.assertEquals([True, False, True, False], calls)

    pred = self.createPredicate(
        test_method_id='true_method',
        membership_criterion_base_category_list=['region'],
        membership_criterion_category_list=['region/other'])
    self.assertFalse(pred.test(doc))
    # Note that if the document is not member of the category, the test_method
    # is not called.
    self.assertEquals([True, False, True, False], calls)
  

  def test_Predicate_getMembershipCriterionCategoryList(self):
    # Predicate_getMembershipCriterionCategoryList is a script used to show the
    # item list in Predicate_view/my_membership_criterion_category_list.
    # When called on a predicate using a simple category (like region) as
    # membership criterion base category, it will show for values the content
    # of this category.
    pred = self.createPredicate(
        membership_criterion_base_category_list=['region'], )
    self.failUnless(('europe/western_europe', 'region/europe/western_europe') in
        [tuple(x) for x in pred.Predicate_getMembershipCriterionCategoryList()],
        pred.Predicate_getMembershipCriterionCategoryList(),)
    
    # If this category is empty, it will show values from fallback category,
    # with the path they have when they are acquired
    pred = self.createPredicate(
        membership_criterion_base_category_list=['source_region'], )
    # note that the id of the actual base category is displayed in the first
    # item too, for making it clear in the UI that it's the content of a
    # category used for another base category.
    self.failUnless(('source_region/europe/western_europe',
                     'source_region/region/europe/western_europe') in
        [tuple(x) for x in pred.Predicate_getMembershipCriterionCategoryList()],
        pred.Predicate_getMembershipCriterionCategoryList(),)


  def test_PredicateFusion(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """Test simple predicates fusion.
    New predicate act as a logical AND between predicates
    """
    if not run : return
    # if both predicates are true, resulting predicate is true
    self.playSequence("""
      stepCreateDocument
      stepSetDocumentFranceRegionMembership
      stepSetDocumentStoreverGroupMembership
      stepCreateRegionFrancePredicate
      stepSaveFirstPredicate
      stepCreateGroupStoreverPredicate
      stepMergePredicates
      stepAssertPredicateTrue
    """)
    # if a predicate is false, resulting predicate is false
    self.playSequence("""
      stepCreateDocument
      stepSetDocumentGermanyRegionMembership
      stepSetDocumentStoreverGroupMembership
      stepCreateRegionFrancePredicate
      stepSaveFirstPredicate
      stepCreateGroupStoreverPredicate
      stepMergePredicates
      stepAssertPredicateFalse
    """)

  def test_PredicateFusionAndTestMethodId(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """Test predicates fusion and test_method_id attribute."""
    if not run : return
    self.playSequence("""
      stepCreateDocument
      stepSetDocumentFranceRegionMembership
      stepCreateRegionFrancePredicate
      stepSaveFirstPredicate
      stepCreatePredicateTrueScript
      stepCreateTestMethodIdPredicate
      stepMergePredicates
      stepAssertPredicateTrue
    """)
    self.playSequence("""
      stepCreateDocument
      stepSetDocumentFranceRegionMembership
      stepCreateRegionFrancePredicate
      stepSaveFirstPredicate
      stepCreatePredicateFalseScript
      stepCreateTestMethodIdPredicate
      stepMergePredicates
      stepAssertPredicateFalse
    """)
    # reverse predicate order, to make sure not only the last one is
    # checked
    self.playSequence("""
      stepCreateDocument
      stepSetDocumentFranceRegionMembership
      stepCreatePredicateFalseScript
      stepCreateTestMethodIdPredicate
      stepSaveFirstPredicate
      stepCreateRegionFrancePredicate
      stepMergePredicates
      stepAssertPredicateFalse
    """)
    # if multiple scripts are defined, they must all return true.
    self.playSequence("""
      stepCreateDocument
      stepSetDocumentFranceRegionMembership
      stepCreatePredicateFalseScript
      stepCreateTestMethodIdPredicate
      stepSaveFirstPredicate
      stepCreatePredicateTrueScript
      stepCreateTestMethodIdPredicate
      stepMergePredicates
      stepAssertPredicateFalse
    """)
    # same in reverse order
    self.playSequence("""
      stepCreateDocument
      stepSetDocumentFranceRegionMembership
      stepCreatePredicateTrueScript
      stepCreateTestMethodIdPredicate
      stepSaveFirstPredicate
      stepCreatePredicateFalseScript
      stepCreateTestMethodIdPredicate
      stepMergePredicates
      stepAssertPredicateFalse
    """)

  def test_MembershipCriterion_SQLQuery(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """
    Make sure that predicate generate valid sql.
    """
    if not run : return

    def test(function):
      """make sure that an exception is not raised"""
      function()
      return True

    predicate_without_membership_values = self.createPredicate(
      membership_criterion_base_category_list=['group'])
    self.assert_(test(predicate_without_membership_values.searchResults))

    predicate_with_membership_values = self.createPredicate(
      membership_criterion_base_category_list=['group'],
      membership_criterion_category_list=GROUP_STOREVER_PATH,
      )
    self.assert_(test(predicate_with_membership_values.searchResults))

  def test_MultiValuedMembershipCriterion_SQLQuery(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """
    Make sure that predicate generate valid sql.
    """
    if not run : return

    def test(function):
      """make sure that an exception is not raised"""
      function()
      return True

    predicate_without_membership_values = self.createPredicate(
      multimembership_criterion_base_category_list=['group'])
    self.assert_(test(predicate_without_membership_values.searchResults))

    predicate_with_membership_values = self.createPredicate(
      multimembership_criterion_base_category_list=['group'],
      membership_criterion_category_list=GROUP_STOREVER_PATH,
      )
    self.assert_(test(predicate_with_membership_values.searchResults))

# TODO :
#  multi membership category
#  asPredicate scripts
#  predicate range
#  predicate + category fusion using setPredicateCategoryList
#  predicate matrix ?

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPredicates))
  return suite

