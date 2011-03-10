The slapos.recipe.erp5 aims to instanciate an ERP5 environnment
===============================================================

SLAP parameters
---------------

activity_node_amount, login_node_amount
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Optional: Yes
:Type: integer
:Default: None
:Description: If any of those is present Zope/Zeo cluster is being created with specialised nodes. Oherwise one simple Zope instance with own ZODB is created.

ca_*
~~~~

:Optional: Yes
:Name: ca_country_code, ca_email, ca_state, ca_city, ca_company
:Type: string
:Default: XX, xx@example.com, State, City, Company
:Description: Certificate Authority configuration.

key_auth_path
~~~~~~~~~~~~~

:Optional: Yes
:Type: string
:Default: /erp5/portal_slap
:Description: Path where connections using PKI authorisation will be directed.
