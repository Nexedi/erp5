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

from zLOG import LOG

class Filter(Implicit):

  def __init__(self, spec=None, filter=None, portal_type=None,
               filter_method=None, filter_node=0, filter_leave=0):
    """
      Initialize attributes. spec and portal_type can be lists, tuples or strings.

      filter_method - filter_method allows for extending filtering in an arbitrary way
                      filter_method must be provided with a category and should
                      return 0 (False) or 1 (True)
      
    """
    #LOG('Filter __init__', 0, 'self = %s, spec = %s, filter = %s, portal_type = %s' % (str(self), str(spec), str(filter), str(portal_type)))
    if type(filter) is type({}):
      self.filter_dict = filter
    else:
      self.filter_dict = {}
    if portal_type is not None:
      if type(portal_type) == type(''):
        portal_type = [portal_type]
      # XXX An empty list or tuple is the same as None here.
      if len(portal_type) > 0:
        self.filter_dict['portal_type'] = portal_type
    if spec is not None:
      if type(spec) == type(''):
        spec = [spec]
      # XXX An empty list or tuple is the same as None here.
      if len(spec) > 0:
        self.filter_dict['meta_type'] = spec
    self.filter_method = filter_method
    self.filter_node = filter_node
    self.filter_leave = filter_leave

  def test(self, context):
    """
      Test filter on a context
    """
    #LOG('Filter test', 0, 'context = %s' % repr(context))
    is_node = None
    if self.filter_node:
      is_node = len(context.contentIds(filter={'portal_type' : 'Category'}))
      if is_node:
        return 0
    if self.filter_leave:
      if is_node is None:
        # Only recalculate is_node if not already done
        is_node = len(context.contentIds(filter={'portal_type' : 'Category'}))
      if not is_node:
        return 0
    for k, v in self.filter_dict.items():
      #LOG('Filter test', 0, "k = %s, v = %s" % (repr(k), repr(v)))
      if type(v) in (type([]), type(())):
        if context.getProperty(k) not in v:
          return 0
      elif context.getProperty(k) != v:
        return 0
    if self.filter_method is not None:
      return self.filter_method(context)
    return 1


  def asDict(self):
    """
      Returns a dictionnary of parameters which can be passed to SQL Catalog
    """
    return self.filter_dict

  def asSQL(self):
    """
      Returns an SQL expression which can be used as a query
    """
    # To be done

  def filter(self, value_list):
    #LOG('Filter filter', 0, 'value_list = %s' % repr(value_list))
    return filter(lambda v: self.test(v), value_list)
