# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################



SYNCML_NAMESPACE = 'SYNCML:SYNCML1.2'
NSMAP = {'syncml': SYNCML_NAMESPACE}

NULL_ANCHOR = '00000000T000000Z'

MAX_OBJECTS = 300
MAX_LEN = 1<<16

XUPDATE_INSERT_LIST = ('xupdate:insert-after', 'xupdate:insert-before')
XUPDATE_ADD = 'xupdate:append'
XUPDATE_DEL = 'xupdate:remove'
XUPDATE_UPDATE = 'xupdate:update'
XUPDATE_ELEMENT = 'xupdate:element'
XUPDATE_INSERT_OR_ADD_LIST = XUPDATE_INSERT_LIST + (XUPDATE_ADD,)

ADD_ACTION = 'Add'
REPLACE_ACTION = 'Replace'

ACTIVITY_PRIORITY = 5

class SynchronizationError(Exception):
  pass
