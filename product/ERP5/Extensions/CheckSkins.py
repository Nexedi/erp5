from Products.ERP5Type.Globals import get_request
import re
import os
import sys
import csv
from Products.CMFCore.utils import expandpath

from zLOG import LOG

try:
    from App.config import getConfiguration
except ImportError:
    getConfiguration = None

if getConfiguration is None:
  data_dir = '/var/lib/zope/data'
else:
  data_dir = getConfiguration().instancehome + '/data'

fs_skin_spec = ('ERP5 Filesystem Formulator Form',
                'ERP5 Filesystem PDF Template',
                'Filesystem Formulator Form',
                'Filesystem Page Template',
                'Filesystem Script (Python)',
                'Filesystem Z SQL Method')

zodb_skin_spec = ('ERP5 Form', 'ERP5 PDF Template', 'Page Template', 'Script', 'Script (Python)','Z SQL Method')

def getSkinPathList(self, spec=fs_skin_spec+zodb_skin_spec):
  path_list = self.portal_skins.getSkinPath(self.portal_skins.getDefaultSkin())
  path_list = path_list.split(',')
  skin_list = []
  for path in path_list:
    if path in ('content', 'content18', 'control', 'generic', 'mailin', 'pro', 'topic', 'zpt_content', 'zpt_control', 'zpt_generic', 'zpt_reporttool', 'zpt_topic'):
      continue
    for id in self.portal_skins[path].objectIds(spec):
      skin_list.append(path + '/' + id)
  return skin_list

def split(name):
  """
    Split the name using an underscore as a separator and
    using the change from lower case to upper case as a separator.

    Example: foo_barBaz -> foo, bar, Baz
  """
  part_list = []
  part = ''
  pc = None
  for c in name:
    if c == '_':
      if len(part) > 0:
        part_list.append(part)
      part = ''
      pc = None
    elif pc is not None and pc.islower() and c.isupper():
      if len(part) > 0:
        part_list.append(part)
      part = c
      pc = None
    else:
      pc = c
      part += c
  if pc is not None:
    part_list.append(part)
  return part_list

def suggestName(name, meta_type):
  """
    Suggest a good name for a given name.
  """
  # Determine the prefix. The default is "Base_".
  i = name.find('_')
  if i < 1:
    prefix = 'Base'
  else:
    # Special treatment for view, print, create and list, because they are used very often.
    # packing list is an exception, because it is confusing (i.e. sale_packing_list_list).
    view_index = name.find('_view')
    print_index = name.find('_print')
    create_index = name.find('_create')
    list_index = name.find('_list')
    packing_list_index = name.find('packing_list_')
    if view_index > 0:
      i = view_index
    elif print_index > 0:
      i = print_index
    elif create_index > 0:
      i = create_index
    elif list_index > 0:
      if packing_list_index > 0:
        i = packing_list_index + 12
      else:
        i = list_index
    part_list = split(name[:i])
    prefix = ''
    for part in part_list:
      prefix += part.capitalize()
    name = name[i+1:]
  if meta_type in ('Filesystem Z SQL Method', 'Z SQL Method'):
    new_name = 'z'
    if name[0] == 'z':
      name = name[1:]
    part_list = split(name)
    for part in part_list:
      new_name += part.capitalize()
  else:
    part_list = split(name)
    new_name = part_list[0].lower()
    for part in part_list[1:]:
      new_name += part.capitalize()
  return prefix + '_' + new_name


def checkSkinNames(self, REQUEST=None, csv=0, all=0):
  """
    Check if the name of each skin follows the naming convention.
  """
  if csv:
    msg = 'Folder,Name,New Name,Meta Type\n'
  else:
    msg = '<html><body>'
  rexp = re.compile('^[A-Z][a-zA-Z0-9]*_[a-z][a-zA-Z0-9]*$')
  rexp_zsql = re.compile('^[A-Z][a-zA-Z0-9]*_z[A-Z][a-zA-Z0-9]*$')
  path_list = getSkinPathList(self)
  bad_list = []
  for path in path_list:
    name = path.split('/')[-1]
    skin = self.portal_skins.restrictedTraverse(path)
    if skin.meta_type in ('Filesystem Z SQL Method', 'Z SQL Method'):
      r = rexp_zsql
    else:
      r = rexp
    if all or r.search(name) is None:
      bad_list.append((path, skin.meta_type))
  if len(bad_list) == 0:
    if not csv:
      msg += '<p>Everything is fine.</p>\n'
  else:
    bad_list.sort()
    if not csv:
      msg += '<p>These %d skins do not follow the naming convention:</p><table width="100%%">\n' % len(bad_list)
      msg += '<tr><td>Folder</td><td>Skin Name</td><td>Meta Type</td></tr>\n'
    i = 0
    for path,meta_type in bad_list:
      name = path.split('/')[-1]
      suggested_name = suggestName(name, meta_type)
      folder = path[:-len(name)-1]
      if (i % 2) == 0:
        c = '#88dddd'
      else:
        c = '#dddd88'
      i += 1
      if csv:
        msg += '%s,%s,%s,%s\n' % (folder, name, suggested_name, meta_type)
      else:
        msg += '<tr bgcolor="%s"><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (c, folder, name, meta_type)
    if not csv:
      msg += '</table>\n'
  if not csv:
    msg += '</body></html>'
  return msg

def fixSkinNames(self, REQUEST=None, file=None, dry_run=0):
  """
    Fix bad skin names.

    This method does:

      - Check all the contents of all skins.

      - Check immediate_view, constructor_path and actions in all portal types.

      - Check skins of all business templates.

      - Check actbox_url in transitions and worklists and scripts of all workflows.

      - Rename skins.
  """
  if REQUEST is None:
    REQUEST = get_request()

  if file is None:
    msg = 'You must put a CSV file inside the data directory, and specify %s/ERP5Site_fixSkinNames?file=NAME \n\n' % self.absolute_url()
    msg += 'The template of a CSV file is available via %s/ERP5Site_checkSkinNames?csv=1 \n\n' % self.absolute_url()
    msg += 'This does not modify anything by default. If you really want to fix skin names, specify %s/ERP5Site_fixSkinNames?file=NAME&dry_run=0 \n\n' % self.absolute_url()
    return msg

  file = os.path.join(data_dir, file)
  file = open(file, 'r')
  class NamingInformation: pass
  info_list = []
  try:
    reader = csv.reader(file)
    for row in reader:
      folder, name, new_name, meta_type = row[:4]
      if len(row) > 4 and len(row[4]) > 0:
        removed = 1
        new_name = row[4]
      else:
        removed = 0
      if meta_type == 'Meta Type': continue
      if name == new_name: continue
      # Check the existence of the skin and the meta type. Paranoid?
      #if self.portal_skins[folder][name].meta_type != meta_type:
      #  raise RuntimeError, '%s/%s has a different meta type' % (folder, name)
      info = NamingInformation()
      info.meta_type = meta_type
      info.folder = folder
      info.name = name
      info.new_name = new_name
      info.regexp = re.compile('\\b' + re.escape(name) + '\\b') # This is used to search the name
      info.removed = removed
      info_list.append(info)
  finally:
    file.close()

  # Now we have information enough. Check the skins.
  msg = ''
  path_list = getSkinPathList(self)
  for path in path_list:
    skin = self.portal_skins.restrictedTraverse(path)
    try:
      text = skin.manage_FTPget()
    except:
      type, value, traceback = sys.exc_info()
      line = 'WARNING: the skin %s could not be retrieved because of the exception %s: %s\n' % (path, str(type), str(value))
      LOG('fixSkinNames', 0, line)
      msg += '%s\n' % line
    else:
      name_list = []
      for info in info_list:
        if info.regexp.search(text) is not None:
          text = info.regexp.sub(info.new_name, text)
          name_list.append(info.name)
      if len(name_list) > 0:
        line = '%s is modified for %s' % ('portal_skins/' + path, ', '.join(name_list))
        LOG('fixSkinNames', 0, line)
        msg += '%s\n' % line
        if not dry_run:
          if skin.meta_type in fs_skin_spec:
            f = open(expandpath(skin.getObjectFSPath()), 'w')
            try:
              f.write(text)
            finally:
              f.close()
          else:
            REQUEST['BODY'] = text
            skin.manage_FTPput(REQUEST, REQUEST.RESPONSE)

  # Check the portal types.
  for t in self.portal_types.objectValues():
    # Initial view name.
    text = t.immediate_view
    for info in info_list:
      if info.name == text:
        line = 'Initial view name of %s is modified for %s' % ('portal_types/' + t.id, text)
        LOG('fixSkinNames', 0, line)
        msg += '%s\n' % line
        if not dry_run:
          t.immediate_view = info.new_name
        break
    # Constructor path.
    text = getattr(t, 'constructor_path', None)
    if text is not None:
      for info in info_list:
        if info.name == text:
          line = 'Constructor path of %s is modified for %s' % ('portal_types/' + t.id, text)
          LOG('fixSkinNames', 0, line)
          msg += '%s\n' % line
          if not dry_run:
            t.constructor_path = info.new_name
          break
    # Actions.
    for action in t.listActions():
      text = action.action.text
      for info in info_list:
        if info.regexp.search(text) is not None:
          text = info.regexp.sub(info.new_name, text)
          line = 'Action %s of %s is modified for %s' % (action.getId(), 'portal_types/' + t.id, info.name)
          LOG('fixSkinNames', 0, line)
          msg += '%s\n' % line
          if not dry_run:
            action.action.text = text
          break

  # Check the portal templates.
  template_tool = getattr(self, 'portal_templates', None)
  # Check the existence of template tool, because an older version of ERP5 does not have it.
  if template_tool is not None:
    for template in template_tool.contentValues(filter={'portal_type':'Business Template'}):
      # Skins.
      skin_id_list = []
      name_list = []
      for skin_id in template.getTemplateSkinIdList():
        for info in info_list:
          if info.name == skin_id:
            name_list.append(skin_id)
            skin_id = info.new_name
            break
        skin_id_list.append(skin_id)
      if len(name_list) > 0:
        line = 'Skins of %s is modified for %s' % ('portal_templates/' + template.getId(), ', '.join(name_list))
        LOG('fixSkinNames', 0, line)
        msg += '%s\n' % line
        if not dry_run:
          template.setTemplateSkinIdList(skin_id_list)
      # Paths.
      path_list = []
      name_list = []
      for path in template.getTemplatePathList():
        for info in info_list:
          if info.regexp.search(path):
            name_list.append(skin_id)
            path = info.regexp.sub(info.new_name, path)
            break
        path_list.append(path)
      if len(name_list) > 0:
        line = 'Paths of %s is modified for %s' % ('portal_templates/' + template.getId(), ', '.join(name_list))
        LOG('fixSkinNames', 0, line)
        msg += '%s\n' % line
        if not dry_run:
          template.setTemplatePathList(path_list)

  # Workflows.
  for wf in self.portal_workflow.objectValues():
    # Transitions.
    for id in wf.transitions.objectIds():
      transition = wf.transitions._getOb(id)
      text = transition.actbox_url
      for info in info_list:
        if info.regexp.search(text) is not None:
          text = info.regexp.sub(info.new_name, text)
          line = 'Transition %s of %s is modified for %s' % (id, 'portal_workflow/' + wf.id, info.name)
          LOG('fixSkinNames', 0, line)
          msg += '%s\n' % line
          if not dry_run:
            transition.actbox_url = text
          break
    # Worklists.
    for id in wf.worklists.objectIds():
      worklist = wf.worklists._getOb(id)
      text = worklist.actbox_url
      for info in info_list:
        if info.regexp.search(text) is not None:
          text = info.regexp.sub(info.new_name, text)
          line = 'Worklist %s of %s is modified for %s' % (id, 'portal_workflow/' + wf.id, info.name)
          LOG('fixSkinNames', 0, line)
          msg += '%s\n' % line
          if not dry_run:
            worklist.actbox_url = text
          break
    # Scripts.
    for id in wf.scripts.objectIds():
      script = wf.scripts._getOb(id)
      text = script.manage_FTPget()
      name_list = []
      for info in info_list:
        if info.regexp.search(text) is not None:
          text = info.regexp.sub(info.new_name, text)
          name_list.append(info.name)
      if len(name_list) > 0:
        line = 'Script %s of %s is modified for %s' % (id, 'portal_workflow/' + wf.id, ', '.join(name_list))
        LOG('fixSkinNames', 0, line)
        msg += '%s\n' % line
        if not dry_run:
          REQUEST['BODY'] = text
          script.manage_FTPput(REQUEST, REQUEST.RESPONSE)

  # Rename the skins.
  if not dry_run:
    for info in info_list:
      try:
        if info.meta_type in fs_skin_spec:
          skin = self.portal_skins[info.folder][info.name]
          old_path = expandpath(skin.getObjectFSPath())
          new_path = info.regexp.sub(info.new_name, old_path)
          if info.removed:
            os.remove(old_path)
          else:
            os.rename(old_path, new_path)
        else:
          folder = self.portal_skins[info.folder]
          if info.removed:
            folder.manage_delObjects([info.name])
          else:
            folder.manage_renameObjects([info.name], [info.new_name])
      except:
        type, value, traceback = sys.exc_info()
        if info.removed:
          line = 'WARNING: the skin %s could not be removed because of the exception %s: %s\n' % (info.name, str(type), str(value))
          LOG('fixSkinNames', 0, line)
          msg += '%s\n' % line
        else:
          line = 'WARNING: the skin %s could not be renamed to %s because of the exception %s: %s\n' % (info.name, info.new_name, str(type), str(value))
          LOG('fixSkinNames', 0, line)
          msg += '%s\n' % line

  return msg