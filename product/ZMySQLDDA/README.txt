Z MySQL Deferred DA

  This is the Z MySQL database deferred adapter product for the 
  Z Object Publishing Environment. It is based on
  ZMySQLDA and follows the same API and installation
  procedure. 
  
  The main difference with ZMySQLDA is that the execution
  of SQL expressions is deferred and executed during the Zope
  commit time rather than immediately. This allows for example
  to group INSERT and DELETE statements in a very short amount of
  time, which reduces risks of lock. It also allows to use
  MyISAM tables without raising useless exception messages related
  to the non transactional nature of MyISAM.
  
  ** IMPORTANT **
  
  SELECT expressions will not work in deferred mode