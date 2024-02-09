##############################################################################
#
# Copyright (c) 2006-2007 Nexedi SA and Contributors. All Rights Reserved.
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

import re


def getLastWorkflowDate(self, state_name='simulation_state', state=('released','public')):
  '''we can make something more generic out of it
  or JP says "there is an API for it" and we trash this one'''
  if not hasattr(self, 'workflow_history'):
    return None
  for wflow in self.workflow_history.values():
    if wflow is None or len(wflow) == 0:
      continue # empty history
    if wflow[0].get(state_name) is None:
      continue # not the right one
    for i in range(len(wflow)):
      ch = wflow[-1-i]
      act = ch.get('action', '')
      if act is not None and act.endswith('action'):
        if ch.get(state_name, '') in state:
          return ch['time']
  return None

#############################################################################
# Mail management
def extractParams(txt):
  """
  extract parameters given in mail body
  We assume that parameters are given as lines of the format:
  name:value
  """
  r = re.compile(r'^([\w_]+):([\w_/]+)$')
  res=[]
  for line in txt.split():
    found=r.findall(line.strip())
    if len(found)==1:
      res.append(found[0])
  return dict(res)
