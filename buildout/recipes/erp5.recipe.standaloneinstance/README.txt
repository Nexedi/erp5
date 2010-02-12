Zope standalone instance
========================

This recipe is useful to create standalone Zope instance independent from
buildout tree.

Specification
=============

This recipe shall provide safe instance creation and updating. It shall mix
Zope level instance creation with ERP5 site bootstrap (erp5.recipe.zope2install
+ erp5.recipe.createsite). On update only filesystem will be *safely* updated
without touch user produced data (mostly from ZODB).

DISCLAIMER
==========
Until some stability will be met everything can change without any further
notice, without backward compatibility, possibly with *removing* existing data
produced by previous versions.
