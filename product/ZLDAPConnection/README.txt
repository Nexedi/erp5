ZopeLDAP README

 ZopeLDAP is based off of work done by Anthony Baxter and also
 Maurice Davice and Scott Robertson at CodeIt.  It is an attempt to
 make LDAP behave more like Zope objects.

 It needs David Leonard's ldapmodule, from http://python-ldap.sourceforge.net/
 and the compiled module needs to be (naturally) in your PYTHONPATH
 (or in ZLDAPConnection/).

 It's been tested against the OpenLDAP stable server release, as at 
 March 14, 1999 and Nov 2, 1999.

IMPORTANT

 There is a known bug in the transactional behavior of the LDAP
 Connection object, and as of 1.1.0 this feature can be turned off.
 The bug could put your ZODB into a nasty state due to a failed
 transaction (usually fixed by just restarting Zope), so it is
 recommended you run with the Transactional ability turned off.  *This 
 bug only occurs when updating more than one Entry object in a single
 transaction space*.

Features

 o Ability to browse an LDAP database like you would browse normal
   folders.
 
 o In 1.1.0, however, the Transactional behavior may be turned off.
   This could speed things up for read-only situations, and is more
   stable than the transactional one.

 o Entry objects obey the rules of Acquisition.

 o In the Zope management interface, LDAPConnections and their
   Entries may be browsed.

 o LDAP Filters provide another way of accessing Entry
   objects.  They behave in a similar fashion to ZSQL Methods, but
   they are *read-only*.  There is no current LDAP Spec for
   update/insert type queries.  *see Caveats below*

 o Improved Entry object API that is Python Script friendly.  For
   updating\adding\deleting new Entry objects, LDAP Filters (to
   retrieve entries) and Python Scripts (to update) go nicely together.


Caveats

 o Lack of stunning documentation.  

 o The only way to strongly protect Entry objects from being written is
   to use a connection name/password to the LDAP Server that does not
   have any write permissions.  Zope security permissions can also be
   used.

 o It currently only supports simple_bind for connecting to the
   server.

 o All Entry attributes come back in the form of a list of strings.
   This is how the LDAP Module (and presumably LDAP in general) does
   this.  Attributes accessed through __getattr__ (like dtml-var
   accesses) come back as an instance of AttrWrap which subclasses
   UserList and whose str() return is a comma seperated list.  (This
   should prevent needing to do 
   '(dtml-in mail)(dtml-var sequence-item)(/dtml-in)' on every
   attribute, especially where one value is expected.

Known Bugs

 o Transactional Behavior breaks when updating more than one Entry
   object per LDAP Connection in a single transaction.  This behavior
   can put the ZODB into a bad state since it fails during the
   two-phase commit, however restarting Zope tends to return things to 
   normal.


Special Thanks

 o Jens Vagelpohl (jens@digicool.com) for getting the pointy-hairs to
   give me time to make 1.1.0 finally happen.

 o Anthony Baxter (anthony@interlink.com.au) for most of the original work

 o Scott Robertson (sropertson@codeit.com) and Maurice Davice
   (mdavis@codeit.com) for theirs too.

 o David Leonard for his LDAP Module and for keeping it pretty much
   in alignment with the RFC (rfc1823).

Author:
  Jeffrey P Shell (jeffrey@Digicool.com)

Original Authors:
  Anthony Baxter (anthony@interlink.com.au)
  Maurice Davice (mdavis@codeit.com)
  Scott Robertson (srobertson@codeit.com)
