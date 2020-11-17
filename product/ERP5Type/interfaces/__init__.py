# -*- coding: utf-8 -*-
# XXX/FIXME: tried to work without explicit definition of all interfaces (this
# file empty) but failed to do so
from __future__ import absolute_import
from .consistency_message import IConsistencyMessage
from .object_message import IObjectMessage
from .action_provider import IAction, IActionContainer
from .cache_plugin import ICachePlugin
from .category_access_provider import ICategoryAccessProvider
from .value_access_provider import IValueAccessProvider
from .constraint import IConstraint
from .role_provider import ILocalRoleAssignor, ILocalRoleGenerator
from .types_tool import ITypesTool, ITypeProvider
