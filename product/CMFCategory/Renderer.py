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


from Filter import Filter

class Renderer(Filter):
  """
    Produces Item list out of category list
  """

  def __init__(self, spec=None, filter={}, portal_type=None,
                     display_id = None, sort_id = None,
                     display_method = None, sort_method = None,
                     is_right_display = 0, translate_display = 0, translatation_domain = None,
                     base_category = None, base=1, display_none_category=0):
    """
    - *display_id*: the id of attribute to "call" to calculate the value to display
                      (getProperty(display_id) -> getDisplayId)

    - *display_method*: a callable method which is used to calculate the value to display

    - *sort_id*: the id of the attribute to "call" to calculate the value used for sorting.
                Sorting is only applied to default ItemList items.

                          self.getProperty(sort_id)
                    foo       3
                    foo1      1
                    foo2      5
          display order will be (foo1, foo, foo2)

    - *sort_method*: a callable method which provides a sort function (à la cmp)

    - *is_right_display*: use the right value in the couple as the display value.

    - *translate_display*: set to 1, we call translation on each item

    - *translatation_domain*: domain to use for translation

    - *recursive*: browse recursively to build the ItemList

    - *base_category*: the base category to consider (if None, default is used) API

    - *base*: if set to 0, do not include the base category. If set to 1,
              include the base category. If set to a string, use the string as base.

              (implementation trick: if set to string, use that string as the base string
              when recursing) IMPLEMENTATION HACK

    - *base*: if set to 0, do not include the base category. If set to 1,
              include the base category. If set to a string, use the string as base.
              This is useful for creationg multiple base categories sharing the same categories.
              (ex. target_region/region/europe)

    - *is_self_excluded*: allows to exclude this category from the displayed list

    - *current_category*: allows to provide a category which is not part of the
                          default ItemList. Very useful for displaying
                          values in a popup menu which can no longer
                          be selected.

    - *display_none_category*: allows to include an empty value. Very useful
                        to define None values or empty lists through
                        popup widgets. If both has_empty_item and
                        current_category are provided, current_category
                        is displayed first.


    """
    Filter.__init__(self, spec=spec, filter=filter, portal_type=portal_type)
    self.display_id = display_id
    self.sort_id = sort_id
    self.display_method = display_method
    self.sort_method = sort_method
    self.is_right_display = is_right_display
    self.translate_display = translate_display
    self.translatation_domain = translatation_domain
    self.base_category = base_category
    self.base = base
    self.display_none_category = display_none_category

  def render(self, category_tool, value_list, current_category):
    """
      Returns rendered items
    """
    value_list = self.filter(value_list)
    if self.sort_method is not None:
      value_list.sort(self.sort_method)
    elif self.sort_id is not None:
      value_list.sort(lambda x,y: cmp(x.getProperty(self.sort_id), y.getProperty(self.sort_id)))

    """
      for b in catalog_search:
        if display_id is None:
          v = base + b.relative_url
          result += [(v,v)]
        else:
          try:
            o = b.getObject()
            v = getattr(o, display_id)()
            result += [(v,base + b.relative_url)]
          except:
            LOG('WARNING: CategoriesTool',0, 'Unable to call %s on %s' % (display_id, b))

      if sort_id is not None:
        result.sort()

    """