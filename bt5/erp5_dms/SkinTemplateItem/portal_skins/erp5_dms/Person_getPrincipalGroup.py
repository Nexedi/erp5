"""
This is to enable customization of obtaining the principal group a person is assigned to,
which is required for proper categorisation of a document contributed by the person.
Default implementation return a group of an organisation acquired through default_career.
Can be changed to return a group from an assignment, or any other way.
"""

return context.getGroup()
