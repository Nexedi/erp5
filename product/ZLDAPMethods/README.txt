Quick README on ZLDAP Filter Methods

 Current

  ZLDAP Filter Methods are a way of executing LDAP Searches according
  to RFC1558 'A String Representation of LDAP Search Filters'.  They
  can be used like ZSQL Methods and use DTML inside of them.  For
  example, one could do a Filter of 'uid=<dtml-var foo>'.  ZLDAP Filter 
  Methods return Entry objects.

ZLDIF Filter Methods
  ZLDIF Filter Methods are a way to generate ldif document which are parsed to modify LDAP database.
  This is a sample of dtml code <dtml-ldifline attr="uidNumber" expr="'03ERRRNN981'" type="string"> 
  for generating valid LDIF message.
