##############################################################################
#
# Copyright (c) 2002-2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from Testing import ZopeTestCase
from zLOG import LOG
import random


import traceback
import linecache
import sys
import re
import six
# Monkey patch traceback system to print how far we get in the current
# sequence.
# This part is adapted from python 2.4's traceback.py
def special_extract_tb(tb, limit = None):
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    list = []
    n = 0
    while tb is not None and (limit is None or n < limit):
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line: line = line.strip()
        else: line = None

        # display where we failed in the sequence
        if co == Sequence.play.__code__:
          if line is None:
            line = ''
          sequence = f.f_locals['self']
          line += '\n    Current Sequence:\n%s' % sequence.asText()
        list.append((filename, lineno, name, line))
        tb = tb.tb_next
        n = n+1
    return list
traceback.extract_tb = special_extract_tb


class Step:

  def __init__(self,method_name='',required=1,max_replay=1):
    self._method_name = method_name
    self._required = required
    self._max_replay = max_replay

  def play(self, context, sequence=None, quiet=True):
    method_name = 'step' + self._method_name
    method = getattr(context,method_name)
    # We can in same cases replay many times the same step,
    # or not playing it at all
    nb_replay = random.randrange(0,self._max_replay+1)
    if self._required:
      if nb_replay==0:
        nb_replay=1
    for i in range(0,nb_replay):
      if not quiet:
        ZopeTestCase._print('\n  Playing step... %s' % self._method_name)
        LOG('Step.play', 0, 'Playing step... %s' % self._method_name)
      method(sequence=sequence)

class Sequence:

  def __init__(self, context=None):
    self._step_list = []
    self._dict = {}
    self._played_index = 0
    self._context = context

  def __getitem__(self, key):
    return self._dict[key]

  def __setitem__(self, key, value):
    self._dict[key] = value

  def __contains__(self, key):
    return key in self._dict

  def asText(self):
    """
    Representation of the current Sequence. Useful for debuggers.
    """
    line_list = []
    for idx, step in enumerate(self._step_list):
      if idx == self._played_index:
        line_list.append('    > %s' % step._method_name)
      else:
        line_list.append('      %s' % step._method_name)
    return '\n'.join(line_list)

  def play(self, context, sequence=None, sequence_number=0, quiet=True):
    if not quiet:
      if self._played_index == 0:
        ZopeTestCase._print('\nStarting New Sequence %i... ' % sequence_number)
        LOG('Sequence.play', 0, 'Starting New Sequence %i... ' % sequence_number)
    if sequence is None:
      while self._played_index < len(self._step_list):
        self._step_list[self._played_index] \
        .play(context, sequence=self, quiet=quiet)
        # commit transaction after each step
        context.commit()
        self._played_index += 1

  def addStep(self,method_name,required=1,max_replay=1):
    new_step = Step(method_name=method_name,
                    required=required,max_replay=max_replay)
    self._step_list.append(new_step)

  def set(self, keyword, value):
    self._dict[keyword] = value

  def edit(self, *args, **kw):
    return self._dict.update(*args, **kw)

  def get(self, key, default=None):
    return self._dict.get(key, default)

  def setdefault(self, key, default=None):
    return self._dict.setdefault(key, default)

  def __call__(self, sequence_string, sequence_number=0, quiet=True):
    """
    add some steps and directly runs them, this allows to easily write
    such code when sequence are unable to handle too complex cases :

      sequence('CreateFoo Tic')
      [some code not using sequences]
      sequence('CreateBar Tic')
    """
    self.setSequenceString(sequence_string)
    if self._context is None:
      raise ValueError('context must be initialized when sequence directly called')
    self.play(self._context, sequence_number=sequence_number, quiet=quiet)

  def setSequenceString(self, sequence_string):
    sequence_string = re.subn("#.*\n", "\n", sequence_string)[0]
    step_list = sequence_string.split()
    self.setSequenceStringList(step_list)

  def setSequenceStringList(self, step_list):
    for step in step_list:
      if step != '':
        if step.startswith('step'):
          step = step[4:]
        self.addStep(step)


class StoredSequence(Sequence):
  """A StoredSequence is a Sequence that can store an ERP5's state into
  a Trash Bin and restore it before before being played. If the state is
  not stored yet, then it will create it then store it.
  This capability is interesting when multiple tests share a same initial
  state, as the state needs to be generated only once and can be reused
  for all of them.
  """

  def __init__(self, context, id):
    Sequence.__init__(self, context)
    self._id = id

  def serialiseSequenceDict(self):
    def _serialise(key, value):
      result_dict = {'key': key}
      if (
          isinstance(value, str) or
          isinstance(value, int) or
          isinstance(value, float) or
          isinstance(value, dict) or
          value is None
        ):
        result_dict['type'] = "raw"
        result_dict['value'] = value
      elif isinstance(value, list):
        result_dict['type'] = "list"
        result_dict['value'] = [_serialise(key, x) for x in value]
      else:
        result_dict['type'] = "erp5_object"
        result_dict['value'] = value.getRelativeUrl()
      return result_dict

    result_list = []
    for key, value in six.iteritems(self._dict):
      result_list.append(_serialise(key, value))
    return result_list

  def deserialiseSequenceDict(self, data):
    portal = self._context.getPortalObject()
    def _deserialise(serialised_dict):
      if serialised_dict["type"] == "raw":
        return serialised_dict["value"]
      elif serialised_dict["type"] == "list":
        return [_deserialise(x) for x in serialised_dict["value"]]
      elif serialised_dict["type"] == "erp5_object":
        return portal.restrictedTraverse(serialised_dict['value'])
      else:
        raise TypeError("Unknown serialised type %s", serialised_dict["type"])

    for serialised_dict in data:
      self._dict[serialised_dict['key']] = _deserialise(serialised_dict)

  def _getTrashBinId(self, context):
    if not context:
      context = self.context
    return "%s_%s" % (context.__class__.__name__, self._id)

  def store(self, context):
    context.login()
    document_dict = context._getCleanupDict()
    trashbin_id = self._getTrashBinId(context)
    if trashbin_id in context.portal.portal_trash:
      context.portal.portal_trash.manage_delObjects(ids=[self._id])
    trashbin_value = context.portal.portal_trash.newContent(
      portal_type="Trash Bin",
      id=trashbin_id,
      title=trashbin_id,
      serialised_sequence=self.serialiseSequenceDict(),
      document_dict=document_dict,
    )
    for module_id, object_id_list in six.iteritems(document_dict):
      for object_id in object_id_list:
        context.portal.portal_trash.backupObject(
          trashbin_value, [module_id], object_id, save=True, keep_subobjects=True
        )
    context.tic()
    context.logout()

  def restore(self, context):
    context.login()
    trashbin_value = context.portal.portal_trash[self._getTrashBinId(context)]
    document_dict = trashbin_value.getProperty('document_dict')
    for module_id, object_id_list in six.iteritems(document_dict):
      for object_id in object_id_list:
        context.portal.portal_trash.restoreObject(
          trashbin_value, [module_id], object_id, pass_if_exist=True
        )
    self.deserialiseSequenceDict(
      trashbin_value.getProperty("serialised_sequence"),
    )
    context.tic()
    context.logout()

  def play(self, context, **kw):
    portal = self._context.getPortal()
    if getattr(portal.portal_trash, self._getTrashBinId(context), None) is None:
      ZopeTestCase._print('\nRunning and saving stored sequence \"%s\" ...' % self._id)
      sequence = Sequence()
      sequence.setSequenceString(context.getSequenceString(self._id))
      sequence.play(context)
      self._dict = sequence._dict.copy()
      self.store(context)
    else:
      ZopeTestCase._print('\nRestoring stored sequence \"%s\" ...' % self._id)
      self.restore(context)
    Sequence.play(self, context, **kw)

class SequenceList:

  def __init__(self):
    self._sequence_list = []

  def addSequence(self, sequence):
    self._sequence_list.append(sequence)

  def addSequenceString(self, sequence_string):
    """
    The sequence string should be a string of method names
    separated by spaces or \n

    returns the sequence for those steps.
    """
    # remove comments in sequence strings
    sequence = Sequence()
    sequence.setSequenceString(sequence_string)
    self.addSequence(sequence)
    return sequence

  def addSequenceStringList(self, step_list):
    sequence = Sequence()
    sequence.setSequenceStringList(step_list)
    self.addSequence(sequence)
    return sequence

  def play(self, context, quiet=True):
    i = 1
    for sequence in self._sequence_list:
      sequence._played_index = 0
      sequence.play(context, sequence_number=i, quiet=quiet)
      i+=1

  def getSequenceList(self):
    return self._sequence_list

