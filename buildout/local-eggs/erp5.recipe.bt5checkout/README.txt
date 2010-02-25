infrae.subversion wrapper for Business Templates
================================================

Easy way to define which Business Templates to download to which folders.

[infrae]
urls =
  http://server/path/SOMETHING/revision SOMETHING

[bt5checkout]
base = http://server/path/
revision = revision
urls =
  SOMETHING # it will become http://server/path/SOMETHING/revision SOMETHING for infrae.subversion
