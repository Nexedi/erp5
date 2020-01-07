
##############################################################################
#
# Copyright (c) 2007-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can rediscaisse_courantebute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is discaisse_courantebuted in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin
from Products.DCWorkflow.DCWorkflow import ValidationFailed

QUIET = False
RUN_ALL_TEST = True

class TestERP5BankingAccountingDate(TestERP5BankingMixin):
  """
    Unit test Accounting Date definition and utility script.
  """


  def getTitle(self):
    return "ERP5BankingAccountingDate"

  def getBaobab_checkAccountingDateOpen(self):
    return getattr(self.getPortal(), 'Baobab_checkAccountingDateOpen')

  def accountingDateCheckFails(self, **kw):
    BankingAccountingDate = self.getBaobab_checkAccountingDateOpen()
    self.assertRaises(ValidationFailed, BankingAccountingDate, **kw)

  def accountingDateCheckSucceeds(self, **kw):
    BankingAccountingDate = self.getBaobab_checkAccountingDateOpen()
    BankingAccountingDate(**kw)

  def afterSetUp(self):
    self.initDefaultVariable()
    self.createManagerAndLogin()
    self.createFunctionGroupSiteCategory(site_list=['paris'])
    self.checkUserFolderType()
    self.organisation = self.organisation_module.newContent(id='baobab_org',
      portal_type='Organisation', function='banking', group='baobab',
      site='testsite/paris', role='internal')
    user_dict = {
      'super_user' : [['Manager'], self.organisation, 'banking/comptable',
                      'baobab',
                      'testsite/paris/surface/banque_interne/guichet_1']
      }
    self.createERP5Users(user_dict)
    self.logout()
    self.loginByUserName('super_user')
    self.accounting_date_site = self.testsite.paris
    self.now = DateTime(DateTime().Date())
    self.past_day = self.now - 1
    self.future_day = self.now + 2 # "+ 2" to make sure test succeeds even if
                                   # current date changes during test.

  def stepNowSucceeds(self, sequence=None, sequence_list=None, **kwd):
    self.accountingDateCheckSucceeds(
      date=self.now,
      site=self.accounting_date_site)
    self.accountingDateCheckSucceeds(
      date=self.future_day,
      site=self.accounting_date_site)
    self.accountingDateCheckFails(
      date=self.past_day,
      site=self.accounting_date_site)

  def stepPastDaySucceeds(self, sequence=None, sequence_list=None, **kwd):
    self.accountingDateCheckSucceeds(
      date=self.now,
      site=self.accounting_date_site)
    self.accountingDateCheckSucceeds(
      date=self.future_day,
      site=self.accounting_date_site)
    self.accountingDateCheckSucceeds(
      date=self.past_day,
      site=self.accounting_date_site)
    self.accountingDateCheckFails(
      date=self.past_day - 1,
      site=self.accounting_date_site)

  def openAccountingDate(self, date=None, site=None):
    TestERP5BankingMixin.openAccountingDate(self, date=date, site=site)

  def stepEmptyAccountingDateModule(self, sequence=None, sequence_list=None,
                                    **kwd):
    accounting_date_module = self.getPortal().accounting_date_module
    object_id_list = [x for x in accounting_date_module.objectIds()]
    accounting_date_module.manage_delObjects(ids=object_id_list)

  def stepCreateTodayAccountingDate(self, sequence=None, sequence_list=None,
                                    **kwd):
    self.openAccountingDate(date=self.now, site=self.accounting_date_site)

  def stepCreatePastDayAccountingDate(self, sequence=None, sequence_list=None,
                                      **kwd):
    self.openAccountingDate(date=self.past_day, site=self.accounting_date_site)

  def test_AccountingDate(self, quiet=QUIET, run=RUN_ALL_TEST):
    if not run:
      return
    sequence_list = SequenceList()
    sequence_string_1 = 'stepEmptyAccountingDateModule ' \
                        'Tic ' \
                        'stepNowSucceeds ' \
                        'stepCreateTodayAccountingDate ' \
                        'Tic ' \
                        'stepNowSucceeds ' \
                        'stepEmptyAccountingDateModule ' \
                        'stepCreatePastDayAccountingDate ' \
                        'Tic ' \
                        'stepPastDaySucceeds '
    sequence_list.addSequenceString(sequence_string_1)
    sequence_list.play(self)

