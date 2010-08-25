It is disallowed to:

 * use hooks directory directly in buildout (eg. assuming that it will exists
   while running buildout)

Rationale: It disallows using buildout in networked environment and extending
           over network.

 * accesing hooks by SVN URI

Rationale: It forces to use SVN structure and makes mirroring and HA hard to
           obtain.
