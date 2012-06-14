# -*- coding: UTF-8 -*-
# Copyright (C) 2000-2002  Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

# Import from Localizer
from LocalAttributes import LocalAttributes, LocalAttribute


class Locale(LocalAttributes):

    # Time, hours and minutes
    time = LocalAttribute('time')

    def time_en(self, datetime):
        return datetime.strftime('%H:%M')

    def time_es(self, datetime):
        return datetime.strftime('%H.%M')
