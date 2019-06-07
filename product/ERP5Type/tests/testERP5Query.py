# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2019 Nexedi SA and Contributors. All Rights Reserved.
#                    Tristan Cavelier <tristan.cavelier@nexedi.com>
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

import unittest
from unittest import skip
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

class TestERP5Query(ERP5TypeTestCase):
  """Test query search text parsing/rendering and document matching.

  The goal is to check that stringified queries are well parsed and
  rendered back to the user (mostly for ERP5JS interface) so that originaly
  searched objects can strictly be retreived again with the rendered search.
  This requires to buildQuery and to render asSearchTextExpression with
  the current configuration of the catalog in order to detect
  inconsistency, for example in the use of backslashes in the current
  full text engine syntax.
  """

  def getTitle(self):
    return "ERP5Query"

  def getBusinessTemplateList(self):
    return ("erp5_full_text_mroonga_catalog", "erp5_base")

  def _createOrganisationOverwrite(self, **kw):
    _id = kw.pop("id")
    organisation = getattr(self.portal.organisation_module, _id, None)
    if organisation is not None:
      self.portal.organisation_module.manage_delObjects(ids=[_id])
    return self.portal.organisation_module.newContent(portal_type="Organisation", id=_id, **kw)

  def _assertQueryKwParsingRenderingMatching(self, query_kw, expected_match_list=None, XXX=False):
    catalog = self.portal.portal_catalog
    sql_catalog = catalog.getSQLCatalog()
    parsed_query = sql_catalog.buildQuery(query_kw)
    generated_sql = catalog(query=parsed_query, src__=1)
    rendered_search_text = parsed_query.asSearchTextExpression(sql_catalog)
    parsed_query_2 = sql_catalog.buildQuery({"search_text": rendered_search_text})
    generated_sql_2 = catalog(query=parsed_query_2, src__=1)

    self.assertEqual(XXX if XXX else generated_sql, generated_sql_2, "{!r} != {!r}\n\ntraceback_info : {!r}".format(
      generated_sql,
      generated_sql_2,
      {
        "query_kw": query_kw,
        "parsed_query": parsed_query,
        "rendered_search_text": rendered_search_text,
        "parsed_query_2": parsed_query_2,
      },
    ))

    if expected_match_list is None:
      return

    expected_match_list = [r.getPath() for r in sorted(expected_match_list, key=lambda o: o.getPath())]
    resulting_match_list = [r.path for r in catalog(query=parsed_query, portal_type="Organisation", uid=[o.getUid() for o in self.organisation_list], sort_on=[("path", "ascending")])]

    self.assertEqual(expected_match_list, resulting_match_list)

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.organisation_list = [
      self._createOrganisationOverwrite(
        id="test_erp5_query_000",
        title="TestERP5QueryBackslashAndText",
      ),
      self._createOrganisationOverwrite(
        id="test_erp5_query_011",
        title="TestERP5QueryBackslash\\AndText",
      ),
      self._createOrganisationOverwrite(
        id="test_erp5_query_012",
        title="TestERP5QueryBackslash\\\\AndText",
      ),
      self._createOrganisationOverwrite(
        id="test_erp5_query_013",
        title="TestERP5QueryBackslash\\\\\\AndText",
      ),
      self._createOrganisationOverwrite(
        id="test_erp5_query_021",
        title="TestERP5QueryBackslash\\",
      ),
      self._createOrganisationOverwrite(
        id="test_erp5_query_022",
        title="TestERP5QueryBackslash\\\\",
      ),
      self._createOrganisationOverwrite(
        id="test_erp5_query_023",
        title="TestERP5QueryBackslash\\\\\\",
      ),
      self._createOrganisationOverwrite(
        id="test_erp5_query_030",
        title="TestERP5QuerySpace AndText",
      ),
    ]
    self.organisation_dict = {o.getId()[len("test_erp5_query_"):]: o for o in self.organisation_list}
    self.tic()

  def test_query_kw_parsing_rendering_and_matching_with_column(self):
    self._assertQueryKwParsingRenderingMatching({'title': 'TestERP5QueryBackslashAndText'}, [self.organisation_dict["000"]])
  def test_query_kw_parsing_rendering_and_matching_with_column_and_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'title': 'TestERP5QueryBackslash\\AndText'}, [self.organisation_dict["011"]])
  def test_query_kw_parsing_rendering_and_matching_with_column_and_2_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'title': 'TestERP5QueryBackslash\\\\AndText'}, [self.organisation_dict["012"]])
  def test_query_kw_parsing_rendering_and_matching_with_column_and_3_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'title': 'TestERP5QueryBackslash\\\\\\AndText'}, [self.organisation_dict["013"]])

  def test_query_kw_parsing_rendering_and_matching_with_column_and_no_ending_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'title': 'TestERP5QueryBackslash'}, [])
  def test_query_kw_parsing_rendering_and_matching_with_column_and_ending_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'title': 'TestERP5QueryBackslash\\'}, [self.organisation_dict["021"]])
  def test_query_kw_parsing_rendering_and_matching_with_column_and_2_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'title': 'TestERP5QueryBackslash\\\\'}, [self.organisation_dict["022"]])
  def test_query_kw_parsing_rendering_and_matching_with_column_and_3_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'title': 'TestERP5QueryBackslash\\\\\\'}, [self.organisation_dict["023"]])

  def test_query_kw_parsing_and_rendering_with_column_and_operator(self):
    self._assertQueryKwParsingRenderingMatching({'title': '<TestERP5Query999'})

  def test_simple_query_parsing_rendering_and_matching_with_column_and_operator(self):
    self._assertQueryKwParsingRenderingMatching({'query': SimpleQuery(title='<TestERP5Query000')}, [])

  def test_search_text_parsing_rendering_and_matching_with_column_and_quote(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:"TestERP5QueryBackslashAndText"'}, [self.organisation_dict["000"]])
  def test_search_text_parsing_rendering_and_matching_with_column_quote_and_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:"TestERP5QueryBackslash\\AndText"'}, [self.organisation_dict["011"]])
  def test_search_text_parsing_rendering_and_matching_with_column_quote_and_2_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:"TestERP5QueryBackslash\\\\AndText"'}, [self.organisation_dict["012"]])
  def test_search_text_parsing_rendering_and_matching_with_column_quote_and_3_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:"TestERP5QueryBackslash\\\\\\AndText"'}, [self.organisation_dict["013"]])

  def test_search_text_parsing_rendering_and_matching_with_column(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QueryBackslashAndText'}, [self.organisation_dict["000"]])
  def test_search_text_parsing_rendering_and_matching_with_column_and_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QueryBackslash\\AndText'}, [self.organisation_dict["011"]])
  def test_search_text_parsing_rendering_and_matching_with_column_and_2_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QueryBackslash\\\\AndText'}, [self.organisation_dict["012"]])
  def test_search_text_parsing_rendering_and_matching_with_column_and_3_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QueryBackslash\\\\\\AndText'}, [self.organisation_dict["013"]])

  @skip('please fix parse(render(parse(invalid_syntax_search_text))) != parse(invalid_syntax_search_text)')
  def test_search_text_parsing_rendering_and_matching_with_column_quote_and_ending_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:"TestERP5QueryBackslash\\"'})
  def test_search_text_parsing_rendering_and_matching_with_column_quote_and_2_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:"TestERP5QueryBackslash\\\\"'})
    # It actually matches [] - should it match "022" instead ? Behavior to be defined
  @skip('please fix parse(render(parse(invalid_syntax_search_text))) != parse(invalid_syntax_search_text)')
  def test_search_text_parsing_rendering_and_matching_with_column_quote_and_3_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:"TestERP5QueryBackslash\\\\\\"'})

  def test_search_text_parsing_rendering_and_matching_with_column_and_ending_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QueryBackslash\\'}, [self.organisation_dict["021"]])
  def test_search_text_parsing_rendering_and_matching_with_column_and_2_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QueryBackslash\\\\'}, [self.organisation_dict["022"]])
  def test_search_text_parsing_rendering_and_matching_with_column_and_3_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QueryBackslash\\\\\\'}, [self.organisation_dict["023"]])

  def test_search_text_parsing_rendering_and_matching_with_quote(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': '"TestERP5QueryBackslashAndText"'}, [self.organisation_dict["000"]])
  def test_search_text_parsing_rendering_and_matching_with_quote_and_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': '"TestERP5QueryBackslash\\AndText"'})
    # It actually matches [self.organisation_dict["000"]] - should it match "011" instead ? Behavior to be defined
  def test_search_text_parsing_rendering_and_matching_with_quote_and_2_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': '"TestERP5QueryBackslash\\\\AndText"'})
    # It actually matches [self.organisation_dict["011"]] - should it match "012" instead ? Behavior to be defined
  def test_search_text_parsing_rendering_and_matching_with_quote_and_3_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': '"TestERP5QueryBackslash\\\\\\AndText"'})
    # It actually matches [self.organisation_dict["011"]] - should it match "013" instead ? Behavior to be defined

  def test_search_text_parsing_rendering_and_matching(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'TestERP5QueryBackslashAndText'}, [self.organisation_dict["000"]])
  def test_search_text_parsing_rendering_and_matching_with_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'TestERP5QueryBackslash\\AndText'})
    # It actually matches [self.organisation_dict["000"]] - should it match "011" instead ? Behavior to be defined
  def test_search_text_parsing_rendering_and_matching_with_2_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'TestERP5QueryBackslash\\\\AndText'})
    # It actually matches [self.organisation_dict["011"]] - should it match "012" instead ? Behavior to be defined
  def test_search_text_parsing_rendering_and_matching_with_3_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'TestERP5QueryBackslash\\\\\\AndText'})
    # It actually matches [self.organisation_dict["011"]] - should it match "013" instead ? Behavior to be defined

  @skip('please fix parse(render(parse(invalid_syntax_search_text))) != parse(invalid_syntax_search_text)')
  def test_search_text_parsing_rendering_and_matching_with_quote_and_ending_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': '"TestERP5QueryBackslash\\"'})
  def test_search_text_parsing_rendering_and_matching_with_quote_and_2_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': '"TestERP5QueryBackslash\\\\"'})
    # It actually matches [self.organisation_dict[k] for k in self.organisation_dict.keys() if k.startswith("01") or k.startswith("02")] - should it really match "021" ? Behavior to be defined
  @skip('please fix parse(render(parse(invalid_syntax_search_text))) != parse(invalid_syntax_search_text)')
  def test_search_text_parsing_rendering_and_matching_with_quote_and_3_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': '"TestERP5QueryBackslash\\\\\\"'})

  def test_search_text_parsing_rendering_and_matching_with_ending_backslash(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'TestERP5QueryBackslash\\'})
    # It actually matches [self.organisation_dict[k] for k in self.organisation_dict.keys() if k.startswith("00") or k.startswith("01") or k.startswith("02")]) - should it really match "000" ? Behavior to be defined
  def test_search_text_parsing_rendering_and_matching_with_2_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'TestERP5QueryBackslash\\\\'})
    # It actually matches [self.organisation_dict[k] for k in self.organisation_dict.keys() if k.startswith("01") or k.startswith("02")]) - should it really match "021" ? Behavior to be defined
  def test_search_text_parsing_rendering_and_matching_with_3_ending_backslashes(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'TestERP5QueryBackslash\\\\\\'})
    # It actually matches [self.organisation_dict[k] for k in self.organisation_dict.keys() if k.startswith("01") or k.startswith("02")]) - should it really match "021" and "022" ? Behavior to be defined

  @skip('please fix parse(render(parse(search_text_with_a_space))) != parse(search_text_with_a_space)')
  def test_search_text_parsing_and_rendering_with_space(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': 'TestERP5QuerySpace AndText'})
  def test_search_text_parsing_and_rendering_with_space_and_quote(self):
    self._assertQueryKwParsingRenderingMatching({'search_text': '"TestERP5QuerySpace AndText"'})

  def test_search_text_parsing_and_rendering_with_column_and_equal(self):  # XXX test it in ZSQLCatalog syntax tree check !
    #self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QuerySpace"AndText'}, XXX=True)  # <SimpleQuery 'SearchableText' mroonga_boolean 'title:TestERP5QuerySpace"AndText'>
    #self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QuerySpace(AndText'}, XXX=True)  # <SimpleQuery 'SearchableText' mroonga_boolean 'title:TestERP5QuerySpace(AndText'>
    #self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QuerySpace)AndText'}, XXX=True)  # <SimpleQuery 'SearchableText' mroonga_boolean 'title:TestERP5QuerySpace)AndText'>
    #self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QuerySpace:AndText'}, XXX=True)  # <SimpleQuery 'SearchableText' mroonga_boolean 'title:TestERP5QuerySpace:AndText'>
    #self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QuerySpace>AndText'}, XXX=True)  # <SimpleQuery 'title' = 'TestERP5QuerySpace>AndText'>
    #self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QuerySpace<AndText'}, XXX=True)  # <SimpleQuery 'title' = 'TestERP5QuerySpace<AndText'>
    #self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QuerySpace!AndText'}, XXX=True)  # <SimpleQuery 'title' = 'TestERP5QuerySpace!AndText'>
    #self._assertQueryKwParsingRenderingMatching({'search_text': 'title:TestERP5QuerySpace=AndText'}, XXX=True)  # <SimpleQuery 'title' = 'TestERP5QuerySpace=AndText'>
    pass

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Query))
  return suite
