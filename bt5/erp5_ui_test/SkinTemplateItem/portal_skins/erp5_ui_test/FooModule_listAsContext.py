"""Test for bug 20171215-133705C

acContext creates a temporary copy of Document with changed Properties.
In related test we ensure that property is resolved before getter because
that is how it works in the old UI.
"""
foo_list = list(context.contentValues())
foo_context_list = [foo.asContext(state="Couscous") for foo in foo_list]

"""
for foo, foo_context in zip(foo_list, foo_context_list):
  context.log("Foo.state {!s}, Foo.getState() {!s}, Foo.asContext().state {!s}, Foo.asContext().getState() {!s}".format(
    foo.getProperty('state'), foo.getState(), getattr(foo_context, 'state'), foo_context.getState()))
"""

return foo_context_list
