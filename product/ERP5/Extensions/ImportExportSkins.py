# Import Export Skins
# XXX Warning XXX
# The file /usr/lib/zope/lib/python/Shared/DC/ZRDB/DA.py
# have to be patched with a manage_FTPget wich contains
# a section <dtml-comment></dtml-comment>

fs_skin_ids = ('erp5_trade', 'erp5_accounting', 'erp5_crm')
fs_skin_spec = ('ERP5 Filesystem Formulator Form',
                'Filesystem Formulator Form',
                'Filesystem Page Template',
                'Filesystem Script (Python)',
                'Filesystem Z SQL Method')
fs_skin_dir = '/var/lib/zope/Products/ERP5/skins'
zodb_skin_ids = ('local_trade', 'local_accounting', 'local_crm')
zodb_skin_spec = ('ERP5 Form', 'Page Template', 'Script', 'Script (Python)','Z SQL Method')

def importSkins(self, REQUEST=None, fs_skin_ids=fs_skin_ids, fs_skin_spec=fs_skin_spec, \
                zodb_skin_ids=zodb_skin_ids, zodb_skin_spec=zodb_skin_spec, \
                fs_skin_dir=fs_skin_dir):
  context = self
  result = '\n@@@ Beginning @@@\n'
  i = 0
  for fs_skin_id in fs_skin_ids:
    zodb_skin_id = zodb_skin_ids[i]
    i += 1
    result += "\n@@@ Working in fs_skin_id %s @@@\n" % fs_skin_id
    for spec in fs_skin_spec:
      for o in context.portal_skins[fs_skin_id].objectValues(spec):
        result += "Working on object : %s\n" % o.id
        try:
          # First convert the skin to text
          text = o.manage_FTPget()
        except:
          result += "| error on %s" % o.id
          text = None
        # Then create a new object
        try:
          new_o = context.portal_skins[zodb_skin_id][o.id]
        except:
          folder = context.portal_skins[zodb_skin_id]
          if spec == 'ERP5 Filesystem Formulator Form':
            folder.manage_addProduct['ERP5Form'].addERP5Form(id = o.id)
          if spec == 'Filesystem Z SQL Method':
            # We have to do many things since there's not a good manage_FTPput
            # for ZSQLMethods, this code is based on the one from
            # Products.CMFCore.FSSQLMethod, method _readFile
            folder.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod(id = o.id,\
              title='', connection_id='', arguments='', template='')
          if spec == 'Filesystem Formulator Form':
            folder.manage_addProduct['ERP5Form'].addERP5Form(id = o.id)
          elif spec == 'Filesystem Page Template':
            folder.manage_addProduct['PageTemplates'].manage_addPageTemplate(id = o.id)
          elif spec == 'Filesystem Script (Python)':
            folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id = o.id)
          try:
            new_o = context.portal_skins[zodb_skin_id][o.id]
          except:
            new_o = None
        if new_o is not None:
          REQUEST['BODY'] = text
          if spec == 'Filesystem Z SQL Method': # XXX We must do specific things for
                                        # ZSQLMethods, have to be removed when
                                        # manage_FTPput for ZSQLMethod will be rewritten
            start = text.rfind('<dtml-comment>')
            end = text.rfind('</dtml-comment>')
            block = text[start+14:end]
            parameters = {}
            for line in block.split('\n'):
              pair = line.split(':',1)
              if len(pair)!=2:
                continue
              parameters[pair[0].strip().lower()]=pair[1].strip()
            # check for required and optional parameters
            max_rows = parameters.get('max_rows',1000)
            max_cache = parameters.get('max_cache',100)
            cache_time = parameters.get('cache_time',0)
            class_name = parameters.get('class_name','')
            class_file = parameters.get('class_file','')
            title = parameters.get('title','')
            connection_id = parameters.get('connection_id','')
            arguments = parameters.get('arguments','')
            start = text.rfind('<params>')
            end = text.rfind('</params>')
            arguments = text[start+8:end]
            #connection_id='MySQL'
            template = text[end+9:]
            while template.find('\n')==0:
              template=template.replace('\n','',1)
            # For Debug
            #result += "\n\nid: %s mr: %s mc: %s ct: %s cn: %s \
            #           cf: %s t: %s ci: %s a: %s t: %s params: %s\n\n\n" % \
            #          (new_o.id,max_rows,max_cache,cache_time,class_name,class_file,title,
            #           connection_id,arguments,template,str(parameters))
            try:
              new_o.manage_edit(title=title,connection_id=connection_id,\
                     arguments=arguments, template=template)
              new_o.manage_advanced(max_rows, max_cache, cache_time, class_name, class_file)
            except:
              result += "\nXXX unable to update this zsql method : %s" % new_o.id
          else:
            try:
              new_o.manage_FTPput(REQUEST, REQUEST.RESPONSE)
            except:
              result += "| error2 on %s" % o.id

          #return new_o.id
          result += "\n%s" % o.id
          # And update it with the text
          #new_o.updateFromText(text)

  return result


def exportSkins(self, REQUEST=None, fs_skin_ids=fs_skin_ids, fs_skin_spec=fs_skin_spec, \
                zodb_skin_ids=zodb_skin_ids, zodb_skin_spec=zodb_skin_spec, \
                fs_skin_dir=fs_skin_dir):
  context = self
  result = ''
  i = 0
  for zodb_skin_id in zodb_skin_ids:
    fs_skin_id = fs_skin_ids[i]
    i += 1
    for spec in zodb_skin_spec:
      for o in context.portal_skins[zodb_skin_id].objectValues(spec):
        # First convert the skin to text
        text = o.manage_FTPget()
        # Determine extension
        if spec == 'ERP5 Form':
          fs_ext = '.form'
        elif spec == 'Script':
          fs_ext = '.py'
        elif spec == 'Script (Python)':
          fs_ext = '.py'
        elif spec == 'Z SQL Method':
          fs_ext = '.zsql'
        elif spec == 'Page Template':
          fs_ext = '.pt'
        else:
          fs_ext = '.unknown'
        # Then create a new file
        fs_file_id = "%s/%s/%s%s" % (fs_skin_dir, fs_skin_id, o.id, fs_ext)
        # And update it with the text
        f = open(fs_file_id,'w')
        f.write(text)
        f.close()
