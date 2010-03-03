# Create an ERP5 instance 
# usage: zopectl run create_erp5_instance [options] [business templates]

import os
from optparse import OptionParser
from urllib import unquote

from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager

parser = OptionParser()
parser.add_option("-p", "--portal_id", dest="portal_id",
                  help="The ID of the Portal", default="erp5")
parser.add_option("--erp5_sql_connection_string",
                  dest="erp5_sql_connection_string",
                  help="Connection String used for ZSQLCatalog "
                       "(use %20 for space)",
                  default="test test")
parser.add_option("--cmf_activity_sql_connection_string",
                  dest="cmf_activity_sql_connection_string",
                  help="Connection String used for CMFActivity")
parser.add_option("--erp5_catalog_storage",
                  dest="erp5_catalog_storage",
                  help="Business Template for Catalog Storage")
parser.add_option("-u", "--initial-user",
                  dest="user_and_pass",
                  help="User and Password, separated by :",
                  default="zope:zope")
parser.add_option("--bt5-path",
                  dest="bt5_path",
                  help="Path to folder containing business templates. "
                  "Can be multiple, separated by commas.",
                  default="bt5")

(options, args) = parser.parse_args()

# cmf activity connection string defaults to zsqlcatalog's one
if not options.cmf_activity_sql_connection_string:
  options.cmf_activity_sql_connection_string = \
            options.erp5_sql_connection_string

# connection strings have to contain a space, for conveniance, this space can
# be replaced by %20 character.
options.erp5_sql_connection_string =\
      unquote(options.erp5_sql_connection_string)
options.cmf_activity_sql_connection_string =\
      unquote(options.cmf_activity_sql_connection_string)

username, password = options.user_and_pass.split(':')

try:
  import transaction
except ImportError:
  class Transaction:
    def commit(self):
      return get_transaction().commit()
  transaction = Transaction()

app = makerequest(app)

user = app.acl_users.getUserById(username)
if user is None:
  uf = app.acl_users
  uf._doAddUser(username, password, ['Manager', 'Member', 'Assignee',
                                     'Assignor', 'Author'], [])
  user = uf.getUserById(username)

newSecurityManager(None, user.__of__(app.acl_users))

portal = getattr(app, options.portal_id, None)
if portal is None:
  print 'Adding ERP5 site %s' % options.portal_id
  app.manage_addProduct['ERP5'].manage_addERP5Site(
              id=options.portal_id,
              erp5_sql_connection_string=options.erp5_sql_connection_string,
              cmf_activity_sql_connection_string=\
                        options.cmf_activity_sql_connection_string,
              erp5_catalog_storage='erp5_mysql_innodb_catalog')

  transaction.commit()
  portal = app._getOb(options.portal_id)

# set preference for erp5_subversion
from App.config import getConfiguration
default_site_preference = portal.portal_preferences.default_site_preference
instance_home = getConfiguration().instancehome
default_site_preference.edit(
  preferred_subversion_working_copy_list=['%s/bt5/' % instance_home])
if default_site_preference.getPreferenceState() == 'disabled':
  default_site_preference.enable()

# install our business templates
bt5_list = []
bt5_path_list = options.bt5_path.split(',')

for arg in args:
  bt_path = None
  for path in bt5_path_list:
    bt_path = os.path.join(path, arg)
    if os.path.exists(bt_path):
      break
    else:
      bt_path = None
  if bt_path is None:
    raise ValueError('Business Template %s not found in paths %s' % (arg,
      options.bt5_path))
  installed_bt = portal.portal_templates.getInstalledBusinessTemplate(arg)
  if installed_bt is not None:
    # XXX this way works only for extracted business template, not for
    # *.bt5 packed business template.
    version = file('%s/bt/version' % bt_path).read().strip()
    revision = file('%s/bt/revision' % bt_path).read().strip()
    if version == installed_bt.getVersion() and \
       revision == installed_bt.getRevision():
      print 'Skipping bt %s' % bt_path
      continue
    else:
      print 'Updating bt %s' % bt_path
  else:
    print 'Installing bt %s' % bt_path
  bt = portal.portal_templates.download(bt_path)
  bt.install(force=True)
  transaction.commit()

transaction.commit()
