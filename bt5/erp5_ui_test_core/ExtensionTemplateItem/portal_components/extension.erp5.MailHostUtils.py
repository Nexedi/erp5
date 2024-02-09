##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                  Rafael Monnerat <rafael@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from ExtensionClass import pmc_init_of
from Products.ERP5Type.tests.utils import DummyMailHostMixin

def setupDummyMailHost(self):
  """Replace Original Mail Host by Dummy Mail Host in a non-persistent way
  and reset the list of already sent messages.

  Copied & pasted from ERP5TypeTestCaseMixin._setUpDummyMailHost
  """
  mailhost = self.getPortalObject().MailHost
  cls = mailhost.__class__
  if not issubclass(cls, DummyMailHostMixin):
    cls.__bases__ = (DummyMailHostMixin,) + cls.__bases__
    pmc_init_of(cls)
  mailhost.reset()
  return "True"  # TODO: zope4py3 Zope does not seem to publish `True` correctly
