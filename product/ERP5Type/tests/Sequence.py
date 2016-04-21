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
        if co == Sequence.play.func_code:
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

  def play(self, context, sequence=None, quiet=1):
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

  def play(self, context, sequence=None, sequence_number=0, quiet=1):
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

  def __call__(self, sequence_string, sequence_number=0, quiet=1):
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

  def play(self, context, quiet=1):
    i = 1
    for sequence in self._sequence_list:
      sequence._played_index = 0
      sequence.play(context, sequence_number=i, quiet=quiet)
      i+=1

  def getSequenceList(self):
    return self._sequence_list

