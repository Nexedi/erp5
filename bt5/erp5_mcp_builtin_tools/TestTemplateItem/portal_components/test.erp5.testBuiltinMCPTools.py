##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import itertools
import math

from erp5.component.test.testMCPService import MCPServiceTestCase


class BuiltinMCPToolsTestMixin:
  def test_listPortalTypes(self):
    with self.connection() as conn:
      text, data = _extract(self._tools_call(conn, "MCP_listPortalTypes", {}))
      self.assertIn("portalTypes", data)
      info_list = data["portalTypes"]
      self.assertGreater(len(info_list), 0)
      for info in info_list:
        self.assertIn(info["id"], text)
        for key in ("id", "allowed", "restricted", "description"):
          self.assertIn(key, info)
      org_info = next((i for i in info_list if i["id"] == "Organisation"))
      portal_types = self.portal.portal_types
      org_description = portal_types["Organisation"].getDescription()
      if org_info["id"] == "Organisation":
        self.assertTrue(org_info["allowed"])
        self.assertFalse(org_info["restricted"])
        self.assertEqual(org_info["description"], org_description)
      self.assertIn("AVAILABLE PORTAL TYPES", text)
      self.assertIn(org_description, text)

  def test_getPortalTypeSchema(self):
    with self.connection() as conn:
      portal_type_id = "Organisation"
      kw = {"portal_type_id": portal_type_id}
      text, data = _extract(self._tools_call(conn, "MCP_getPortalTypeSchema", kw))
      self.assertIn("COLUMN SCHEMA FOR: %s" % portal_type_id, text)
      self.assertEqual(data["portal_type"], portal_type_id)
      self.assertGreater(len(data["columns"]), 0)
      column_map = self.portal.PortalType_getColumnMap(
        portal_type_id, ["%s Module" % portal_type_id]
      )
      for column in column_map.values():
        title = column["title"]
        self.assertIn(title, data["columns"])
        self.assertIn(title, text)
        col_data = data["columns"][title]
        for key, value in column.items():
          if key in ("name", "title"):
            continue  # name and title are collapsed together in data send to
            # client, because client doesn't care about id but not all columns
            # have a name
          self.assertEqual(value, col_data[key])

  def test_listPortalType(self):
    # Create test data
    organisation_list = []
    reference_prefix = "tBMCPTOrga"
    for i in range(200):
      reference = "%s_%s" % (reference_prefix, "{:03d}".format(i))
      organisation_list.append(self.newOrganisation(reference))
    organisation_list[-1].invalidate()
    organisation_list.append(self.newOrganisation("TestORG0"))
    organisation_list[-1].invalidate()
    self.tic()

    # Run tests
    with self.connection() as conn:
      self._lpt_filter(conn, organisation_list)
      self._lpt_filter_wildcard(conn, organisation_list, reference_prefix)
      self._lpt_multifilter(conn, reference_prefix)
      self._lpt_column_list(conn)
      self._lpt_sort_on(conn)
      self._lpt_err_bad_portal_type(conn)

  def _lpt_filter(self, conn, organisation_list):
    organisation = organisation_list[0]
    title = organisation.getTitle()
    text, data = self._listPortalType(conn, filters={"Usual Name": title})
    self.assertIn(title, text)
    self._lpt_assertOneColumn(data)
    row = data["rows"][0]
    self.assertEqual(row["Usual Name"], title)

  def _lpt_filter_wildcard(self, conn, organisation_list, reference_prefix):
    # UID sorting is not reliable, because UID order != creation order => sort
    #  instead by title
    sort_on = [["Usual Name", "ascending"]]
    filters = {"Usual Name": reference_prefix + "%"}
    organisation_list = [
      o for o in organisation_list
      if o.getTitle().startswith(reference_prefix)
    ]
    organisation_count = len(organisation_list)
    page_count = int(math.ceil(float(organisation_count) / PAGE_SIZE))
    for page_index in range(page_count):
      text, data = self._listPortalType(
        conn, filters=filters, sort_on=sort_on, page=page_index
      )
      self.assertEqual(data["count"], organisation_count)
      start = page_index * PAGE_SIZE
      end = min(start + PAGE_SIZE, organisation_count)
      self.assertEqual(data["start"], start)
      self.assertEqual(data["end"], end)
      row_list = data["rows"]
      self.assertEqual(len(row_list), end - start)
      for row, org in zip(row_list, organisation_list[start:]):
        validation_state = org.getValidationState().capitalize()
        self.assertIn(org.getTitle(), text)
        self.assertIn(validation_state, text)
        self.assertEqual(row["Usual Name"], org.getTitle())
        self.assertEqual(row["State"], validation_state)

  def _lpt_multifilter(self, conn, reference_prefix):
    filters = {
      "Usual Name": reference_prefix + "%", "State": "Invalidated"
    }
    text, data = self._listPortalType(conn, filters=filters)
    self.assertIn("Invalidated", text)
    self._lpt_assertOneColumn(data)
    row = data["rows"][0]
    self.assertEqual(row["State"], "Invalidated")
    self.assertTrue(row["Usual Name"].startswith(reference_prefix))

  def _lpt_column_list(self, conn):
    column_list = ["uid", "Usual Name", "State", "Site"]
    combinations = itertools.chain.from_iterable(
      itertools.combinations(column_list, r) for r in range(1, len(column_list))
    )
    for combination in combinations:
      text, data = self._listPortalType(conn, column_list=combination)
      row = data["rows"][0]
      self.assertEqual(len(row), len(combination))
      for column in column_list:
        t = self.assertIn if column in combination else self.assertNotIn
        t(column, text)
        t(column, row)

  def _lpt_sort_on(self, conn):
    for order, t in (("ascending", "Less"), ("descending", "Greater")):
      t = getattr(self, "assert%s" % t)
      sort_on = [["uid", order]]
      text, data = self._listPortalType(
        conn, sort_on=sort_on, column_list=["uid"]
      )
      for r0, r1 in zip(data["rows"], data["rows"][1:]):
        uid0, uid1 = r0["uid"], r1["uid"]
        t(uid0, uid1)
        self.assertLess(text.index(uid0), text.index(uid1))

  def _lpt_err_bad_portal_type(self, conn):
    portal_type_id = "Not existing Portal Type Id"
    kw =  {"portal_type_id": portal_type_id}
    result = self._tools_call(conn, "MCP_listPortalType", kw)
    m = [
      "is not contained in any module!",
      "Use MCP_listPortalTypes to find all supported/known portal types"
    ]
    self.assertToolError(result, contains=m)

  def _lpt_assertOneColumn(self, data):
    self.assertEqual(data["count"], 1)
    self.assertEqual(data["start"], 0)
    self.assertEqual(data["end"], 1)
    self.assertEqual(len(data["rows"]), 1)

  def _listPortalType(self, conn, **kw):
    portal_type_id = "Organisation"
    kw.setdefault("portal_type_id", portal_type_id)
    text, data = _extract(self._tools_call(conn, "MCP_listPortalType", kw))
    self.assertEqual(data["portal_type"], portal_type_id)
    return text, data

  def newOrganisation(self, reference):
    parent = self.portal.organisation_module
    organisation = self.newContent(
      parent,
      portal_type="Organisation",
      reference=reference,
      id=reference,
      title=reference,
      description="This is a test organisation with the ref %s" % reference,
    )
    organisation.validate()
    return organisation


PAGE_SIZE = 100  # hard coded in MCP_listPortalType


class BuiltinMCPToolsTestCase(MCPServiceTestCase):
  def afterSetUp(self):
    self.tool_list = [
      self.portal.portal_callables[tool_id] for tool_id in [
        "MCP_listPortalType",
        "MCP_listPortalTypes",
        "MCP_getPortalTypeSchema",
      ]
    ]
    MCPServiceTestCase.afterSetUp(self)


class TestBuiltinMCPTools20250326(BuiltinMCPToolsTestCase, BuiltinMCPToolsTestMixin):
  protocol_version = "2025-03-26"


class TestBuiltinMCPTools20250618(BuiltinMCPToolsTestCase, BuiltinMCPToolsTestMixin):
  protocol_version = "2025-06-18"


class TestBuiltinMCPTools20251125(BuiltinMCPToolsTestCase, BuiltinMCPToolsTestMixin):
  protocol_version = "2025-11-25"


def _extract(result):
  return result["content"][0]["text"], result['structuredContent']
