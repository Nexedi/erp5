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

class Step:

  def __init__(self,method_name='',required=1,max_replay=1):
    self._method_name = method_name
    self._required = required
    self._max_replay = max_replay

  def play(self,context,sequence=None):
    method_name = 'step' + self._method_name
    method = getattr(context,method_name)
    # We can in same cases replay many times the same step,
    # or not playing it at all
    nb_replay = random.randrange(0,self._max_replay+1)
    if self._required:
      if nb_replay==0:
        nb_replay=1
    for i in range(0,nb_replay):
      ZopeTestCase._print('\n  Playing step... %s' % self._method_name)
      LOG('Step.play',0,'Playing step... %s' % self._method_name)
      method(sequence=sequence)
    
class Sequence:

  def __init__(self):
    self._step_list = []
    self._dict = {}

  def play(self,context,sequence=None,sequence_number=0):
    ZopeTestCase._print('\nStarting New Sequence %i... ' % sequence_number)
    LOG('Sequence.play',0,'Starting New Sequence %i... ' % sequence_number)
    if sequence is None:
      for step in self._step_list:
        step.play(context,sequence=self)
        # commit transaction after each step
        get_transaction().commit()

  def addStep(self,method_name,required=1,max_replay=1):
    new_step = Step(method_name=method_name,
                    required=required,max_replay=max_replay)
    self._step_list.append(new_step)

  def set(self, keyword,value):
    self._dict[keyword]=value

  def edit(self, **kw):
    for k, v in kw.items():
      self._dict[k]=v

  def get(self, keyword):
    if self._dict.has_key(keyword):
      return self._dict[keyword]
    return None

class SequenceList:

  def __init__(self):
    self._sequence_list = []

  def addSequence(self,sequence):
    self._sequence_list.append(sequence)

  def addSequenceString(self,sequence_string):
    """
    The sequence string should be a string of method names
    separated by spaces or \n
    """
    step_list = sequence_string.split()
    self.addSequenceStringList(step_list)

  def addSequenceStringList(self,step_list):
    step_list
    sequence = Sequence()
    for step in step_list:
      if step != '':
        if step.startswith('step') : 
          step = step[4:]
        sequence.addStep(step)
    self.addSequence(sequence)

  def play(self, context):
    i = 1
    for sequence in self._sequence_list:
      sequence.play(context,sequence_number=i)
      i+=1

