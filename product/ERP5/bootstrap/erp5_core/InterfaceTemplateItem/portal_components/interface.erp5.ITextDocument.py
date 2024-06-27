# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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

class ITextDocument(Interface):
  """
  TextDocument interface specification

  Document which implement ITextDocument can handle text content in multiple
  format (html, structured-text, text).

  Substitution mapping can occurs on result if
  text_content_substitution_mapping_method_id is defined.

  Substitutions are made using python string templates described by PEP-0292
  ( https://www.python.org/dev/peps/pep-0292 ). The substitution is done using
  "safe_subsitute" method, ie. in the case of missing variables, the substitution
  marker will be kept as-is. To make missing variables an error, one can either
  define the text_content_substitution_mapping_ignore_missing property to False
  on the text document, or pass safe_substitute=False to methods.
  """

  def getTextContent(default=None):
    """
    return text_content from text_content, content filled by user online
    """

  def getTextContentSubstitutionMappingMethodId(default=None):
    """
    return mapping for string substitution
    """

