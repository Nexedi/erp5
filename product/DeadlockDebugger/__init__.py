# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: __init__.py,v 1.1 2005/02/23 15:35:21 fguillaume Exp $

"""Debug running threads

This adds a ZServer hook so that if a special URL is called, a full dump
with tracebacks of the running python threads will be made.

You MUST configure zope.conf before use.
"""
from __future__ import absolute_import

from zLOG import LOG, INFO, ERROR
from App.config import getConfiguration

config = getConfiguration()
if getattr(config, 'product_config', None) is not None:
    deadlockdebugger = config.product_config.get('deadlockdebugger')
    dump_url = ''
    secret = ''
    if deadlockdebugger is None:
        LOG('DeadlockDebugger', ERROR, 'Missing configuration statement '
          '<product-config deadlockdebugger>, not activated')
    else:
        if not 'dump_url' in deadlockdebugger:
            LOG('DeadlockDebugger', ERROR, 'Please configure dump_url and '
                'optionally secret in <product-config deadlockdebugger>, not '
                'activated')
        else:
            from . import dumper
            LOG('DeadlockDebugger', INFO, "Installed")
