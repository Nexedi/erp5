##############################################################################
#
# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.
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

from DateTime import DateTime
from erp5.component.test.testTaskReporting import TestTaskReportingMixin

class TestResearchItemSummaryReport(TestTaskReportingMixin):
  """
  Test Research Items Reports
  """

  def getTitle(self):
    return "ResearchItemSummaryReport"

  def afterSetUp(self):
    """Make sure to initialize needed categories
    """
    super(TestResearchItemSummaryReport, self).afterSetUp()
    ledger_base_category = self.portal.portal_categories.ledger
    for category_id in ("operation", "research"):
      if category_id not in ledger_base_category:
        ledger_base_category.newContent(
             portal_type='Category', title=category_id.title(),
             reference=category_id, id=category_id)

    # create items
    if 'Item_1' not in self.portal.research_item_module:
      self.portal.research_item_module.newContent(title="Item_1",
           id="Item_1", portal_type="Research Item")
    if 'Item_2' not in self.portal.research_item_module:
      self.portal.research_item_module.newContent(title="Item_2",
           id="Item_2", portal_type="Research Item")

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    bt_list = super(TestResearchItemSummaryReport, self).getBusinessTemplateList()
    return list(bt_list) + ["erp5_research_item"]

  def _makeOneTask(self, **kw):
    task =super(TestResearchItemSummaryReport, self)._makeOneTask(
            resource='product_module/development',
            source_section='organisation_module/Organisation_1',
            destination='organisation_module/Organisation_2',
            destination_section='organisation_module/Organisation_2',
            source_project='project_module/Project_1/Line_1',
            start_date=DateTime('2013/01/10'),
            stop_date=DateTime('2013/02/15'),
            ledger="research",
            simulation_state="confirmed",
            **kw)
    return task

  def testResearchSummaryReport(self):
    """
    Test research summary report available on item research module
    """
    report = self.portal.research_item_module.ResearchItemModule_callResearchSummaryReport
    def callReport():
      return report(from_date=from_date, at_date=at_date, batch_mode=True,
                    ledger="research", simulation_state_list=["confirmed"])
    def getDataResult(result):
      data_list = []
      column_id_list = [x[0] for x in result.column_list]
      self.assertEqual(column_id_list[0], "source_title")
      self.assertEqual(column_id_list[-1], "total")
      column_id_list.pop(0)
      column_id_list.pop(-1)
      column_id_list.sort()
      column_id_list = ["source_title"] + column_id_list + ["total"]
      for line in result.listbox_line_list:
        line_data = []
        for property_name in column_id_list:
          line_data.append(line.getProperty(property_name))
        data_list.append(line_data)
      data_list.sort(key=lambda x: x[0])
      column_list = [x for x in result.column_list]
      column_list.sort(key=lambda x: column_id_list.index(x[0]))
      return [x[1] for x in column_list], data_list

    # First call it when it is empty
    from_date = DateTime("2013/01/01")
    at_date = DateTime("2014/01/01")
    result = callReport()
    # Initially we should have only one line for an empty total
    self.assertEqual((["Worker", "Undefined", "Total"],
                      [["Total", None, None]]),
                      getDataResult(result))

    # Then create one task with no item, see if we it is displayed in the report
    self._makeOneTask(
          title='Task 1',
          task_line_quantity=3,
          source='person_module/Person_1',
          )
    result = callReport()
    self.assertEqual((["Worker", "Undefined", "Total"],
                       [["Person_1", 3, 3],
                       ["Total", 3, 3]]),
                      getDataResult(result))

    # Then create one task with item, see if we it is displayed in the report
    self._makeOneTask(
          title='Task 2',
          task_line_quantity=5.2,
          source='person_module/Person_2',
          line_aggregate_relative_url='research_item_module/Item_1',
          )
    result = callReport()
    self.assertEqual((["Worker",   "Undefined", "Item_1", "Total"],
                       [["Person_1",     3,        None,        3],
                        ["Person_2",  None,         5.2,      5.2],
                        ["Total",        3,         5.2,      8.2]]),
                      getDataResult(result))

    # 3 additional tasks to check sums
    self._makeOneTask(
          title='Task 3',
          task_line_quantity=2.4,
          source='person_module/Person_2',
          line_aggregate_relative_url='research_item_module/Item_1',
          )
    self._makeOneTask(
          title='Task 4',
          task_line_quantity=1.7,
          source='person_module/Person_1',
          line_aggregate_relative_url='research_item_module/Item_2',
          )
    self._makeOneTask(
          title='Task 5',
          task_line_quantity=0.9,
          source='person_module/Person_2',
          line_aggregate_relative_url='research_item_module/Item_2',
          )
    result = callReport()
    self.assertEqual((["Worker",   "Undefined", "Item_1", "Item_2", "Total"],
                       [["Person_1",     3,        None,      1.7,     4.7],
                        ["Person_2",  None,         7.6,      0.9,     8.5],
                        ["Total",        3,         7.6,      2.6,    13.2]]),
                      getDataResult(result))



