##############################################################################
#
# Copyright (c) 2018 Nexedi KK and Contributors. All Rights Reserved.
#                    Yusei Tahara <yusei@nexedi.com>
#                    Tatuya Kamada <tatuya@nexedi.com>
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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
from DateTime import DateTime

def _parseCategory(category):
  if category is None or category.find('/') < 0:
    return (category, '')
  split_category = category.split('/')
  return (split_category[0], '/'.join(split_category[1:]))

def toDateTime(time):
  if isinstance(time, float):
    return DateTime(time)
  elif hasattr(time, 'timeTime'):
    # assume that the time is persistent.TimeStamp
    return DateTime(time.timeTime())
  raise ValueError('do not know the time type :%r' % time)

def _getWorkflowHistory(document, initial_datetime):
  history = []
  workflow_history = getattr(document, 'workflow_history', None)
  if workflow_history is None:
    return history
  for workflow_id in workflow_history:
    if workflow_id == 'edit_workflow':
      continue
    record_list = workflow_history[workflow_id]
    acceptable_record_list = []
    for record in record_list:
      try:
        if record['time'] >= initial_datetime:
          acceptable_record_list.append(record)
      except KeyError:
        continue

    for record in acceptable_record_list:
      state = None
      dict_ = {'datetime':record['time'],
               'user':record['actor'] or '',
               'action':record['action'] or '',
               'changes':{}
              }
      for key in record:
        if key.endswith('state'):
          state = record[key]
          break
      if state is not None:
        dict_['changes'][workflow_id] = state
      history.append(dict_)
  return history

def _getRecordedPropertyHistory(document, size):
  recorded_property = getattr(document, '_recorded_property_dict', None)
  if recorded_property is None:
    return []
  return getChangeHistoryList(recorded_property, size=size)

def _getAttributeHistory(document, size, attribute_name):
  if (attribute_name is None) or (attribute_name == '_recorded_property_dict'):
    return []
  attribute = getattr(document, attribute_name, None)
  if attribute is None:
    return []
  return getChangeHistoryList(attribute, size=size)

def getChangeHistoryList(document, size=50, attribute_name=None):
  """
    Returns ZODB History

    Keyword arguments:
    size -- How long history do you need
    attribute_name -- The attribute that you want to show additionary
  """
  connection = document._p_jar
  result = document._p_jar.db().history(document._p_oid, size=size)
  if result is None:
    return []
  result = list(reversed(result))
  initial_datetime = toDateTime(result[0]['time'])
  history = []
  previous_state = None
  for d_ in result:
    current_state = connection.oldstate(document, d_['tid'])
    changes = {}
    current_datetime = toDateTime(d_['time'])
    record = {'datetime':current_datetime,
              'user':d_['user_name'],
              'action':d_['description'],
              'changes':changes
              }
    if previous_state is None:
      previous_state = {}
    for key in current_state:
      if key == 'workflow_history' or key == 'categories':
        continue
      if previous_state.get(key) != current_state[key]:
        changes[key] = current_state[key]
    previous_categories = set(previous_state.get('categories') or ())
    current_categories = set(current_state.get('categories') or ())
    for removed in previous_categories.difference(current_categories):
      ck, cv = _parseCategory(removed)
      changes['-' + ck] = cv
    for added in current_categories.difference(previous_categories):
      ck, cv = _parseCategory(added)
      changes[ck] = cv
    history.append(record)
    previous_state = current_state

  history.extend(_getWorkflowHistory(document, initial_datetime))
  history.extend(_getRecordedPropertyHistory(document, size))
  history.extend(_getAttributeHistory(document, size, attribute_name))
  history.sort(key=lambda x:x['datetime'])

  return history

def getHistoricalRevisionsDateList(document, size=50):
  """
  Returns the list dates in float format for the last
  50 versions of the document.
  """
  result = document._p_jar.db().history(document._p_oid, size)
  return [d_['time'] for d_ in result]

def getRevisionFromDate(document, date, size=50):
  """
  Returns the attribute/property dict of an object from its revision date

  params:
    date - It shold be in float format (or float converted to string)
    size -- How long history do you need
  """
  result = document._p_jar.db().history(document._p_oid, size)
  # Get the version of object using the date
  result_obj = [l for l in result if str(l['time']) == str(date)][0]

  # Return the history state of the object
  connection = document._p_jar
  return connection.oldstate(document, result_obj['tid'])
