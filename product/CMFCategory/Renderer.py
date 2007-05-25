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


from Products.CMFCategory.Filter import Filter
from ZODB.POSException import ConflictError
from zLOG import LOG, PROBLEM

class Renderer(Filter):
  """
    Produces Item list out of category list

    FIXME: translation
    ( update: translation is not implemented in Renderer but in calling
      methods, so maybe it should be removed from this API ? -jerome)
  """

  def __init__(self, spec = None, filter = None, portal_type = None,
                     display_id = None, sort_id = None,
                     display_method = None, sort_method = None, filter_method = None,
                     filter_node=0, filter_leave=0,
                     is_right_display = 0, translate_display = 0,
                     translatation_domain = None, display_base_category = 0,
                     base_category = None, base = 1,
                     display_none_category = 1, current_category = None,**kw):
    """
    - *display_id*: the id of attribute to "call" to calculate the value to display
                      (getProperty(display_id) -> getDisplayId)

    - *display_method*: a callable method which is used to calculate the value to display

    - *filter_method*: a method to filter items in the list

    - *filter_node*: do not keep node categories

    - *filter_leave*: do not keep leave categories

    - *sort_id*: the id of the attribute to "call" to calculate the value used for sorting.
                Sorting is only applied to default ItemList items.

                          self.getProperty(sort_id)
                    foo       3
                    foo1      1
                    foo2      5
          display order will be (foo1, foo, foo2)

    - *sort_method*: a callable method which provides a sort function (?la cmp)

    - *is_right_display*: use the right value in the couple as the display value.

    - *translate_display*: set to 1, we call translation on each item

    - *translatation_domain*: domain to use for translation

    - *display_base_category*: set to 1, display base_category before display
      value

    - *recursive*: browse recursively to build the ItemList

    - *base_category*: the base category to consider (if None, default is used) API

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
    Filter.__init__(self, spec=spec, filter=filter,
                    portal_type=portal_type, filter_method=filter_method,
                    filter_node=filter_node, filter_leave=filter_leave)
    self.display_id = display_id
    self.sort_id = sort_id
    self.display_method = display_method
    self.sort_method = sort_method
    self.is_right_display = is_right_display
    self.translate_display = translate_display
    self.translatation_domain = translatation_domain
    self.display_base_category = display_base_category
    self.base_category = base_category
    self.base = base
    self.display_none_category = display_none_category
    self.current_category = current_category

  def getObjectList(self, value_list):
    new_value_list = []
    for value in value_list:
      obj = value.getObject()
      if obj is not None:
        new_value_list.append(obj)
    return new_value_list

  def render(self, value_list):
    """
      Returns rendered items
    """
    value_list = self.getObjectList(value_list)
    value_list = self.filter(value_list)
    if self.sort_method is not None:
      value_list.sort(self.sort_method)
    elif self.sort_id is not None:
      value_list.sort(lambda x,y: cmp(x.getProperty(self.sort_id), y.getProperty(self.sort_id)))

    # If base=1 but base_category is None, it is necessary to guess the base category
    # by heuristic.
#    if self.base and self.base_category is None:
#      base_category_count_map = {}
#      for value in value_list:
#        if not getattr(value, 'isCategory', 0):
#          continue
#        b = value.getBaseCategoryId()
#        if b in base_category_count_map:
#          base_category_count_map[b] += 1
#        else:
#          base_category_count_map[b] = 1
#      guessed_base_category = None
#      max_count = 0
#      for k,v in base_category_count_map.items():
#        if v > max_count:
#          guessed_base_category = k
#          max_count = v
#      LOG('render', 100, repr(guessed_base_category))

    # Initialize the list of items.
    item_list = []
    if self.current_category:
      if self.is_right_display:
        item = [None, self.current_category]
      else:
        item = [self.current_category, None]
      item_list.append(item)
    if self.display_none_category:
      if self.is_right_display:
        item = ['', '']
      else:
        item = ['', '']
      item_list.append(item)

    for value in value_list:
      #LOG('Renderer', 10, repr(value))
      # Get the label.
      if self.display_method is not None:
        label = self.display_method(value)
      elif self.display_id is not None:
        try:
          label = value.getProperty(self.display_id)
        except ConflictError:
          raise
        except:
          LOG('CMFCategory', PROBLEM, 'Renderer was unable to call %s on %s'
               % (self.display_id, value.getRelativeUrl()))
          label = None
      else:
        label = None
      # Get the url.
      url = value.getRelativeUrl()
      if self.base:
        if self.base_category:
          # Prepend the specified base category to the url.
          url = self.base_category + '/' + url
        else:
          # If the base category of this category does not match the guessed
          # base category, merely ignore this category.
          # This is not the job for a Renderer to automatically remove values
          # if we do not specify a filter
          if getattr(value, 'getBaseCategoryId', None) is not None:
            continue
          # Remove from now, it might be outdated and useless
          #if value.getBaseCategoryId() != guessed_base_category:
          #  continue
      else:
        if self.base_category:
          # Nothing to do.
          pass
        else:
          # Get rid of the base category of this url, only if this is a category.
          if getattr(value, 'isCategory', 0):
            b = value.getBaseCategoryId()
            url = url[len(b)+1:]
      # Add the pair of a label and an url.
      if label is None:
        label = url
      # Add base category in label
      if self.display_base_category:
        if self.base_category:
          bc = value.portal_categories.resolveCategory(self.base_category)
          label = '%s/%s' % (bc.getTitleOrId(), label)
        else:
          if getattr(value, 'getBaseCategoryValue', None) is not None:
            bc = value.getBaseCategoryValue()
            label = '%s/%s' % (bc.getTitleOrId(), label)

      if self.is_right_display:
        item = [url, label]
      else:
        item = [label, url]
      item_list.append(item)

    return item_list
