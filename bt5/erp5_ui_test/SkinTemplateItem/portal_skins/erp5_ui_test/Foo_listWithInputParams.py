"""Foo_listWithInputParams is here only to test passing parameters from REQUEST via introspection in RenderJS UI.

We expect DateTime parameters thus they have to undergo a serialization/deserialization process.
"""

from DateTime import DateTime

assert isinstance(start_date, DateTime), "start_date is instance of {!s} instead of DateTime!".format(type(start_date))
assert isinstance(stop_date, DateTime), "stop_date is instance of {!s} instead of DateTime!".format(type(stop_date))

return context.listFolder(portal_type='Foo Line')
