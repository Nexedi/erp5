import os, shutil
import unittest

import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.backportUnittest import skip

class TestNewStyleClasses(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return 'erp5_base',

  def testImportNonMigratedPerson(self):
    """
    Import a .zexp containing a Person created with an old
    Products.ERP5Type.Document.Person.Person type
    """
    file_name = 'non_migrated_person.zexp'
    import Products.ERP5Type.tests as test_module
    test_path = test_module.__path__
    if isinstance(test_path, list):
      test_path = test_path[0]

    zexp_path = os.path.join(test_path, 'input', file_name)
    self.assertTrue(os.path.exists(zexp_path))

    import_path = os.path.join(os.environ['INSTANCE_HOME'], 'import')
    if not os.path.exists(import_path):
      os.mkdir(import_path)
    shutil.copy(zexp_path, import_path)


    person_module = self.getPortal().person_module
    person_module.manage_importObject(file_name)

    transaction.commit()

    non_migrated_person = person_module.non_migrated_person
    # check that object unpickling instanciated a new style object
    from erp5.portal_type import Person as erp5_document_person
    self.assertEquals(non_migrated_person.__class__, erp5_document_person)

  def testMigrateOldObjectFromZODB(self):
    """
    Load an object with ERP5Type.Document.Person.Person from the ZODB
    and check that migration works well
    """
    from Products.ERP5Type.Document.Person import Person

    # remove temporarily the migration
    from Products.ERP5Type.Utils import PersistentMigrationMixin
    PersistentMigrationMixin.migrate = 0

    person_module = self.getPortal().person_module
    obj_id = "this_object_is_old"
    old_object = Person(obj_id)
    person_module._setObject(obj_id, old_object)
    old_object = person_module._getOb(obj_id)

    transaction.commit()
    self.assertEquals(old_object.__class__.__module__, 'Products.ERP5Type.Document.Person')
    self.assertEquals(old_object.__class__.__name__, 'Person')

    self.assertTrue(hasattr(old_object.__class__, '__setstate__'))

    # unload/deactivate the object
    old_object._p_invalidate()

    # From now on, everything happens as if the object was a old, non-migrated
    # object with an old Products.ERP5Type.Document.Person.Person

    # now turn on migration
    PersistentMigrationMixin.migrate = 1

    # reload the object
    old_object._p_activate()

    self.assertEquals(old_object.__class__.__module__, 'erp5.portal_type')
    self.assertEquals(old_object.__class__.__name__, 'Person')

  def testChangeMixin(self):
    """
    Take an existing object, change the mixin definitions of its portal type.
    Check that the new methods are there.
    """
    portal = self.getPortal()
    person_module = portal.person_module
    person = person_module.newContent(id='John Dough', portal_type='Person')

    person_type = portal.portal_types.Person
    self.assertEquals(person_type.getTypeMixinList(), None)

    try:
      self.assertEquals(getattr(person, 'asText', None), None)
      # just use a mixin/method that Person does not have yet
      person_type.setTypeMixin('TextConvertableMixin')

      transaction.commit()

      self.assertNotEquals(getattr(person, 'asText', None), None)
    finally:
      # reset the type
      person_type.setTypeMixin(None)

  def testChangeDocument(self):
    """
    Take an existing object, change its document class
    Check that the new methods are there.
    """
    portal = self.getPortal()
    person_module = portal.person_module
    person = person_module.newContent(id='Eva Dough', portal_type='Person')

    person_type = portal.portal_types.Person
    self.assertEquals(person_type.getTypeClass(), 'Person')

    try:
      self.assertEquals(getattr(person, 'getCorporateName', None), None)
      # change the base type class
      person_type.setTypeClass('Organisation')

      transaction.commit()

      self.assertNotEquals(getattr(person, 'getCorporateName', None), None)
    finally:
      # reset the type
      person_type.setTypeClass('Person')

TestNewStyleClasses = skip("portal type classes code is not yet committed")(TestNewStyleClasses)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNewStyleClasses))
  return suite
