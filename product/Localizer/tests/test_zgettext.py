# -*- coding: UTF-8 -*-
# Copyright (C) 2001, 2002 J. David Ibáñez <j-david@noos.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Test suite for the zgettext.py script.
"""

# Import from the Standard Library
import os
import sys
import unittest
from unittest import TestCase, TestSuite, TextTestRunner

# Import from Localizer
sys.path.append(os.path.join(sys.path[0], '../'))
import zgettext


class GettextTagTestCase(TestCase):
    def test_caseSimple(self):
        """Test the 'dtml-gettext' tag without any option."""
        text = "<dtml-gettext>\n" \
               "  message\n" \
               "</dtml-gettext>"

        assert zgettext.parse_dtml(text) == ['message']

    def test_caseVerbatim(self):
        """Test the 'dtml-gettext' tag when using the 'verbatim' option."""
        text = "<dtml-gettext verbatim>\n" \
               "  message\n" \
               "</dtml-gettext>"

        assert zgettext.parse_dtml(text) == ['\n  message\n']



if __name__ == '__main__':
    unittest.main()
