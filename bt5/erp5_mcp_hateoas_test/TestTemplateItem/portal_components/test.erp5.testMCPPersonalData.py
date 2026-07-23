##############################################################################
# Tests for Base_stripPersonalData, the personal-data redaction policy applied
# to MCP tool results (portal_skins/erp5_mcp). The policy is what
# MCPService._stripPersonalData calls when a service has strip_personal_data
# enabled, so every test here feeds it a payload in one of the shapes the read
# tools produce -- catalog rows, {"value": ...} field wrappers, nested trees --
# and asserts on what survives.
#
# The generic policy is one rule: a personal record is masked down to its
# name, and nothing else in a result is touched. The rule woelfel states on
# top of it is tested in test.woelfel.testWoelfelPersonalData.
##############################################################################

import copy

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


MASK = "[redacted]"


class TestPersonalDataPolicy(ERP5TypeTestCase):
  """The portal type decides whose record it is; the name survives regardless.

  GDPR protects natural persons, so what is masked follows from WHOSE record a
  value belongs to. A property name cannot carry that: a Person and an
  Organisation hold identically named properties ('default_email_text',
  'default_address_street_address'), so any name-based blacklist masks company
  data and keeps person data by turns.

  The name is the one exception, and it is exempt in both directions -- kept
  on the personal record itself, and never masked on anybody else's document
  for pointing at one. A search whose rows read "[redacted]" leaves the read
  tools with no answer to give, and buys little: the name is already spread
  over every document the same authenticated user may read.
  """

  def getTitle(self):
    return "MCP Personal Data Policy"

  def strip(self, data):
    """Apply the policy the way MCPService._stripPersonalData does.

    Reached through its skin folder rather than by acquisition, so that the
    test does not depend on which skin selection is current.
    """
    policy = self.portal.portal_skins["erp5_mcp"]["Base_stripPersonalData"]
    return policy.__of__(self.portal)(data)

  def assertUntouched(self, data):
    """Returned equal to what went in, and not mutated on the way."""
    expected = copy.deepcopy(data)
    self.assertEqual(self.strip(data), expected)
    self.assertEqual(data, expected)

  # -- the personal record --------------------------------------------------

  def test_person_keeps_its_name_and_loses_everything_else(self):
    data = {
      "relative_url": "person_module/1",
      "portal_type": "Person",
      "title": "Doe, Jane",
      "first_name": "Jane",
      "last_name": "Doe",
      "default_email_text": "jane@example.invalid",
      "default_address_street_address": "Musterweg 3",
      "reference": "jdoe",
      "a_property_no_policy_has_ever_heard_of": "secret",
    }
    result = self.strip(data)
    self.assertEqual(result["title"], "Doe, Jane")
    self.assertEqual(result["first_name"], "Jane")
    self.assertEqual(result["last_name"], "Doe")
    self.assertEqual(result["default_email_text"], MASK)
    self.assertEqual(result["default_address_street_address"], MASK)
    self.assertEqual(result["reference"], MASK)   # a login, not a name
    self.assertEqual(result["a_property_no_policy_has_ever_heard_of"], MASK)

  def test_scaffolding_survives(self):
    """Mask how a record is addressed and it stops being usable at all."""
    data = {
      "relative_url": "person_module/1",
      "uid": 12345,
      "id": "1",
      "portal_type": "Person",
      "translated_portal_type": "Person",
      "parent": "Persons",
      "views": [{"name": "view", "title": "View"}],
      "actions": [{"name": "post_query", "title": "Post a Query"}],
      "first_name": "Jane",
    }
    result = self.strip(data)
    for key in ("relative_url", "uid", "id", "portal_type",
                "translated_portal_type", "parent", "views", "actions"):
      self.assertEqual(result[key], data[key], key)

  def test_person_sub_object_masked_by_containment(self):
    """Addresses, careers and assignments live inside the Person.

    None of these types is listed anywhere: they are personal because of the
    module they are in.
    """
    for portal_type in ("Address", "Career", "Assignment"):
      data = {
        "relative_url": "person_module/1/whatever",
        "portal_type": portal_type,
        "street_address": "Musterweg 3",
        "group_title": "a/group",
        "salary": "90000",
      }
      result = self.strip(data)
      self.assertEqual(result["street_address"], MASK, portal_type)
      self.assertEqual(result["group_title"], MASK, portal_type)
      self.assertEqual(result["salary"], MASK, portal_type)

  def test_organisation_keeps_company_contact_data(self):
    """A supplier's switchboard and billing address are not personal data."""
    self.assertUntouched({
      "relative_url": "organisation_module/1",
      "portal_type": "Organisation",
      "title": "An Organisation",
      "default_telephone_coordinate_text": "+49 931 1234",
      "default_email_text": "info@example.invalid",
      "default_address_street_address": "Some Street 1",
    })

  def test_same_portal_type_opposite_outcome(self):
    """An Address is personal or not depending only on whose it is."""
    person_address = {
      "relative_url": "person_module/1/default_address",
      "portal_type": "Address",
      "street_address": "Musterweg 3",
    }
    organisation_address = {
      "relative_url": "organisation_module/1/default_address",
      "portal_type": "Address",
      "street_address": "Some Street 1",
    }
    self.assertEqual(self.strip(person_address)["street_address"], MASK)
    self.assertEqual(
      self.strip(organisation_address)["street_address"], "Some Street 1"
    )

  def test_person_nested_in_an_organisation_is_still_masked(self):
    data = {
      "relative_url": "organisation_module/1",
      "portal_type": "Organisation",
      "default_email_text": "info@example.invalid",
      "children": [{
        "relative_url": "person_module/1",
        "portal_type": "Person",
        "first_name": "Jane",
        "default_email_text": "jane@example.invalid",
      }],
    }
    result = self.strip(data)
    self.assertEqual(result["default_email_text"], "info@example.invalid")
    self.assertEqual(result["children"][0]["first_name"], "Jane")
    self.assertEqual(result["children"][0]["default_email_text"], MASK)

  def test_field_wrapper_keeps_its_metadata(self):
    """erp5_read returns {"value": ...}: mask the value, not the wrapper."""
    data = {
      "relative_url": "person_module/1",
      "portal_type": "Person",
      "fields": {
        "my_first_name": {
          "type": "StringField", "editable": True, "value": "Jane",
        },
        "my_default_address_street_address": {
          "type": "TextAreaField", "editable": True, "value": "Musterweg 3",
          "title": "Street Address",
        },
      },
    }
    field_dict = self.strip(data)["fields"]
    self.assertEqual(field_dict["my_first_name"]["value"], "Jane")
    masked = field_dict["my_default_address_street_address"]
    self.assertEqual(masked["value"], MASK)
    self.assertEqual(masked["type"], "TextAreaField")
    self.assertEqual(masked["title"], "Street Address")
    self.assertTrue(masked["editable"])

  # -- everybody else's document --------------------------------------------

  def test_relation_fields_still_name_what_they_point_at(self):
    """Masking these was tried and withdrawn: it is what made reads useless."""
    self.assertUntouched({
      "relative_url": "sale_order_module/1",
      "portal_type": "Sale Order",
      "fields": {
        "my_source_decision_title": {
          "type": "RelationStringField",
          "editable": True,
          "title": "Seller",
          "value": {
            "portal_types": ["Person", "Organisation"],
            "urls": ["person_module/1"],
            "value": ["Doe, Jane"],
          },
        },
      },
    })

  def test_denormalised_party_columns_are_kept(self):
    """A party's name on a trade document is that document's, and it stays.

    Resolving these through the catalog is what the policy used to spend most
    of itself on; there is nothing left to resolve.
    """
    self.assertUntouched({
      "count": 2,
      "has_more": False,
      "results": [
        {
          "relative_url": "sale_order_module/1",
          "portal_type": "Sale Order",
          "destination_section_title": "Doe, Jane",
          "source_decision_title": "Doe, John",
          "source_decision_reference": "jdoe",
        },
        {
          "relative_url": "sale_order_module/2",
          "portal_type": "Sale Order",
          "destination_section_title": "An Organisation",
        },
      ],
    })

  def test_undeclared_type_is_not_masked(self):
    """The declaration must not leak into unrelated documents."""
    self.assertUntouched({
      "relative_url": "sale_order_module/1",
      "portal_type": "Sale Order",
      "title": "a title",
      "reference": "ORDER/008.B001",
      "total_price": 1350.0,
      "is_shipped": True,
      "comment": None,
    })

  def test_listbox_metadata_survives(self):
    """'portal_type' in listbox metadata is a LIST of allowed types.

    It describes a form, not a record. Classifying a record by hashing that
    value raises TypeError on the list, and every hand-built payload above
    would miss it.
    """
    self.assertUntouched({
      "relative_url": "person_module/1",
      "portal_type": "Person",
      "all_listboxes": {"listbox": {
        "portal_type": [["Address", "Address"], ["Email", "Email"]],
        "columns": [["title", "Title"], ["asText", "Value"]],
        "default_sort": [["int_index", "Index"]],
        "title": "Contacts",
      }},
    })

  # -- the declaration ------------------------------------------------------

  def test_every_declared_type_is_masked(self):
    """Base_getPersonalDataTypeList is the one declaration everything follows."""
    declared_type_list = list(self.portal.Base_getPersonalDataTypeList())
    self.assertIn("Person", declared_type_list)  # generic ERP5 declares this
    for portal_type in declared_type_list:
      data = {
        "relative_url": "a_module/1",
        "portal_type": portal_type,
        "title": "a title",
        "quantity": 30,
      }
      result = self.strip(data)
      self.assertEqual(result["title"], "a title", portal_type)  # the name
      self.assertEqual(result["quantity"], MASK, portal_type)

  def test_content_of_a_declared_type_module_is_masked(self):
    """Containment comes from the DERIVED module, so sub-objects are covered.

    Nothing enumerates 'Internal Supply Line' or 'Address'; they are masked
    because of where they live.
    """
    for portal_type in self.portal.Base_getPersonalDataTypeList():
      try:
        module = self.portal.getDefaultModule(portal_type)
      except Exception:
        continue                      # a type without a module of its own
      if module is None:
        continue
      data = {
        "relative_url": "%s/1/sub_object_1" % module.getId(),
        "portal_type": "Some Generic Line",
        "quantity": 30,
      }
      self.assertEqual(self.strip(data)["quantity"], MASK, portal_type)

  def test_declared_types_exist(self):
    """A typo would be silently harmless -- and silently unprotected."""
    for portal_type in self.portal.Base_getPersonalDataTypeList():
      self.assertIsNotNone(
        self.portal.portal_types.getTypeInfo(portal_type),
        "no such portal type: %s" % portal_type,
      )
