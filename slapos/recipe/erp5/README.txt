The slapos.recipe.erp5 aims to instanciate an ERP5 environnment
===============================================================

SLAP parameters
---------------

zope_amount
~~~~~~~~~~~

:Optional: Yes
:Type: integer
:Default: None
:Description: If present switches to Zope/ZEO configuration and configures this amount of Zopes connected to ZEO. If not present only one Zope with own ZODB is created.

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
