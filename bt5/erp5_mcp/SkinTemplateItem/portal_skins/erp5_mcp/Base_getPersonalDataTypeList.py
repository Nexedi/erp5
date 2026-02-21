"""Portal types whose documents are personal data (GDPR).

The one declaration Base_stripPersonalData follows: a record of one of these
types, or living in the module of one, is masked down to its name.

A policy derives each type's module with getDefaultModule(), so whatever lives
inside such a document -- an Address held by a Person -- is covered by where
it sits, without being enumerated here.

Generic ERP5 knows only the Person. An instance adds its own by shadowing this
script from a skin folder that comes earlier in the skin path (portal_skins
resolves by that order, so a project folder overloads this one) -- typically
where the portal type is generic but every document of it is about an
individual employee. A project that shadows the policy as well writes its own
rules against this same list.
"""
return (
  "Person",
)
