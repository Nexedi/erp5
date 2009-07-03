##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from zope.interface import Interface

class IBusinessCompletable(Interface):
  """Business Completable interface specification

  Business states and path can be completed or partially completed.
  """
  def isCompleted(explanation):
    """True if all related simulation movements for this explanation
    document are delivered and in simulation state which is considered
    as finished.

    Completed means that it is possible to move to next step of Business Process
    """

  def isPartiallyCompleted(explanation):
    """True if some related simulation movements for this explanation
    document are delivered and in simulation state which is considered
    as finished.
    """

  def isFrozen(explanation):
    """True if all related simulation movements for this explanation
    are frozen.

    Frozen means that simulation movement cannot be modified.
    """

  def getExpectedCompletionDate(task):
    """Returns the date at which the given state is expected to
    be completed, based on the start_date and stop_date of
    the given task document.

    'task' is a document which follows the ITaskGetter interface
    (getStartDate, getStopDate)
    """

  def getExpectedCompletionDuration(task):
    """Returns the duration at which the state is expected to be completed,
    based on the start_date and stop_date of the explanation document.

    'task' is a document which follows the ITaskGetter interface
    (getStartDate, getStopDate)
    """

  def getRemainingTradePhaseList(explanation, trade_phase_list=None):
    """
      Returns the list of remaining trade phases which to be done on the
      explanation.

      trade_phase_list -- if provided, the result is filtered by it after
                          being collected
    """
