from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002,2007 Nexedi SA and Contributors. All Rights Reserved.
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

from ..Common.SQLJoblib import SQLJoblib as _SQLJoblib
from .SQLDict import SQLDict


class SQLJoblib(_SQLJoblib, SQLDict):

  def createTableSQL(self):
    return """\
CREATE TABLE %s (
  uid INTEGER NOT NULL,
  date TEXT NOT NULL,
  path TEXT NOT NULL,
  active_process_uid INTEGER,
  method_id TEXT NOT NULL,
  processing_node INTEGER NOT NULL DEFAULT -1,
  priority INTEGER NOT NULL DEFAULT 0,
  group_method_id TEXT NOT NULL DEFAULT '',
  tag TEXT NOT NULL,
  signature BLOB NOT NULL,
  serialization_tag TEXT NOT NULL,
  retry INTEGER NOT NULL DEFAULT 0,
  message BLOB NOT NULL,
  PRIMARY KEY (uid)
);
\0
CREATE INDEX IF NOT EXISTS %s_idx_processing_node_priority_date ON %s (processing_node, priority, date);
\0
CREATE INDEX IF NOT EXISTS %s_idx_node_group_priority_date ON %s (processing_node, group_method_id, priority, date);
\0
CREATE INDEX IF NOT EXISTS %s_idx_serialization_tag_processing_node ON %s (serialization_tag, processing_node);
\0
CREATE INDEX IF NOT EXISTS %s_idx_path ON %s (path);
\0
CREATE INDEX IF NOT EXISTS %s_idx_active_process_uid ON %s (active_process_uid);
\0
CREATE INDEX IF NOT EXISTS %s_idx_method_id ON %s (method_id);
\0
CREATE INDEX IF NOT EXISTS %s_idx_tag ON %s (tag);
""" % ((self.sql_table,) * 15)
