##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

Base18 is a Zope product which allows to build multilingual portals. It uses
Localizer and extends the Zope CMFDefault product to provide a way
to translate documents at a sentence per sentence level.

It implements a new kind of CMF document: Translations. Translations allow to
store a .po file which allows to translate a given document. This approach
was inspired by the poxml approach used by the "KDE":http://www.kde.org project
to translate its documentation.

Because it works at the sentence or paragraph level, it is possible to use
the fuzzy feature of gettext to find similar translations for a given sentence
and accelerate the translation process.

Base18 also includes a translation workflow which allows to keep track
of translations and their association to documents in a portal.

Base18 is currently much of a "proof-of-concept" which needs to be extended.
Future versions will include greater flexibility and will implement relations.

More information can be found on the "Nexedi":http://www.nexedi.org/software
site::

    http://www.nexedi.org/software
