#!/bin/bash

#CVS_USER=seb
CVS_USER=anonymous

ANON_CVS=anonymous

LOGGED=0
ZERO=0

export CVS_RSH=ssh

for f in CMFActivity CMFCategory ERP5 ERP5Catalog \
         ERP5Form ERP5SyncML ERP5Type ZSQLCatalog \
         ERP5OOo ERP5Security erp5_bt5 erp5_banking
  do
    echo "XXXXX Updating..." $f
    if ls /usr/lib/zope/lib/python/Products/$f > /dev/null 2>&1 /dev/null; then
      cd /usr/lib/zope/lib/python/Products/$f && \
        cvs update -RdP && cd /usr/lib/zope/lib/python/Products/
    else
      if [ $CVS_USER == $ANON_CVS ] ; then
        if [ $LOGGED == $ZERO ] ; then
          cvs -d:pserver:anonymous@cvs.erp5.org:/cvsroot login
          cvs -z3 -d:pserver:anonymous@cvs.erp5.org:/cvsroot co $f
          LOGGED=1
        else
          cvs -z3 -d:pserver:anonymous@cvs.erp5.org:/cvsroot co $f
        fi
      else
        cvs -z3 -d $CVS_USER@cvs.erp5.org:/cvsroot co $f
      fi
    fi
  done

