##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                   Philippe Beaumont <pb@nexedi.com>
#                   Jean-Paul Smets <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
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

ZSQLCatalog is an extension to the traditional Zope ZCatalog and Indexes.
It currently implements an Index which uses an SQL database as external storage.
It allows to query a Zope Catalog with a combination of traditional Zope
Catalog queries (field based, text based) and with complex queries implemented
as SQL methods.

By using ZSQLCatalog, it is possible to develop a whole system with an object
oriented approach and forget about external relational databases yet provide
to users the usual experience of SQL queries.

This Zope product was implemented as a subproject of the ERP5 project in
order to add complex queries to the Zope Object Database without using
an external database for attributes storage.

It is currently much of a "proof-of-concept" which needs to be extended.
Future versions will include greater flexibility and will implement relations.

More information can be found on the "Nexedi":http://www.nexedi.org/software site::

    http://www.nexedi.org/software