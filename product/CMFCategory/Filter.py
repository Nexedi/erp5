##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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


from Acquisition import Implicit

class Filter(Implicit):

  def __init__(self, spec=None, filter={}, portal_type=None):
    """
      A fil
    """
    if type(filter) is type({}):
      self.filter = filter
    else:
      self.filter = {}
    if portal_type is not None:
      self.filter['portal_type'] = portal_type
    if spec is not None:
      self.filter['meta_type'] = spec

  def test(self, context):
    """
      Test filter on a context
    """
    for k, v in self.filter.items():
      if type(v) in (type([]), type(())):
        if context.getProperty(k) not in v:
          return 0
      elif context.getProperty(k) != v:
        return 0
    return 1


  def asDict(self):
    """
      Returns a dictionnary of parameters which can be passed to SQL Catalog
    """
    return self.filter

  def asSql(self):
    """
      Returns an SQL expression which can be used as a query
    """
    # To be done

  def filter(self, value_list):
    return filter(lambda v: self.test(v), value_list)
