
from OFS import Folder,Image
from Globals import HTMLFile, MessageDialog
from AccessControl import getSecurityManager, Permissions

import os
import re
import string
import tempfile
import types

import StringIO
import zipfile
import ZipImporter

# check zip file names for:
filenamepattern=re.compile(r'[A-Za-z0-9][\w\_\-\.]*$')

MINZIPFILESIZE=22


manage_addZipFolderForm=HTMLFile('zipfolderAdd', globals())


def manage_addZipFolder(self, id, title='',
                          file=None,
                          subfolders=0,
                          REQUEST=None):
    """Add a new ZipFolder object with id *id*, uploading file.

    """
    id=str(id)
    id, title = Image.cookId(id, '', file)

    ob=ZipFolder()
    ob.id=id


    self._setObject(id, ob)
    ob=self._getOb(id)

    checkPermission=getSecurityManager().checkPermission


    if file is not None:
        if not checkPermission('Add Documents, Images, and Files', ob):
            raise 'Unauthorized', (
                  'You are not authorized to add DTML Documents.'
                  )
        return ob.manage_upload(file,subfolders,REQUEST=REQUEST)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)



class ZipFolder(Folder.Folder, ZipImporter.ZipImporter):
    """Ein Ordner mit einer Erweiterung, um seinen Inhalt
    und seine Attribute in Form einer ZIP-Datei hochladen
    zu konnen."""

    meta_type="ZipFolder"

    __ac_permissions__=(
        (Permissions.view_management_screens,
         ('manage_uploadForm',)),
        ('Change ZipFolders',
         ('manage_upload','manage_uploadForm')))

    
    manage_options=(Folder.Folder.manage_options+
                    ({ "label": "Upload",
                       "action": "manage_uploadForm"},)
                    )


    manage_uploadForm=HTMLFile('zipfolderUpload', globals())
    

    def manage_upload(self,file='',subfolders=0,replace=0,REQUEST=None, RESPONSE=None):
        """Accept a file and load it up"""

        if isinstance(file,types.StringType):
            if REQUEST: return MessageDialog(
                title  ='Success!',
                message='But no ZIP file.',
                action ='manage_main')
            return # anyway
        
        
        
        # check file sizes
        file.seek(0,2)
        fsize=file.tell()
        file.seek(0,0)

        if fsize == 0:
            if RESPONSE:
                RESPONSE.redirect('manage_main')
            return # anyway

        if replace:
            if subfolders:
                self._remove_objects(metatypes=('DTML Document','Image',
                                                'File','Folder'))
            else:
                self._remove_objects(metatypes=('DTML Document','Image',
                                                'File'))

        self._v_skipped=[]
        self._v_subfolders=subfolders
        self.import_zipfile(file)
        
        if REQUEST:
            if len(self._v_skipped)>0:
                return MessageDialog(
                    title  ='Success!',
                    message=('ZIP file uploaded successfully, '+
                             'some files/folders ignored:<br>'+
                             string.join(self._v_skipped,'<br>')),
                    action ='manage_main')
            else:
                return MessageDialog(
                    title  ='Success!',
                    message='ZIP file uploaded successfully',
                    action ='manage_main')

        if len(self._v_skipped) > 0:
            return self._v_skipped

        return None


            
    def _remove_objects(self,metatypes):
        """Removes old objects from the folder"""
        
        removelist=self.objectIds(metatypes)
        self.manage_delObjects(ids=removelist)

    def add_file(self,path,basename,sf):
        
        if not filenamepattern.match(basename):
            return # skip ugly files
        
        suffix=os.path.splitext(basename)[1]

        folder=self

        if self._v_subfolders:
            folder=self._get_subfolder(path)

        if folder:
            if string.lower(suffix) in ['.htm', '.html']:
                # this is ugly
                sfx=StringIO.StringIO(self._edit_html(sf.getvalue()))
                sf.close()
                folder.manage_addDTMLDocument(id=basename, title='', file=sfx)

            elif string.lower(suffix) in ['.gif', '.jpg', '.jpeg', '.png']:
                folder.manage_addImage(id=basename, title='', file=sf)

            elif len(suffix)==0 and basename[-5:] == "_html":
                folder.manage_addDTMLDocument(id=basename, title='', file=sf)
                
            else:
                self._add_other_file(folder,path,basename,sf)

                
    def _get_subfolder(self,path):

        dirlist = []
        rest = ""
        while path != rest:
            rest=path
            (path,dir)=os.path.split(path)
            if dir != "":
                dirlist.append(dir)

        dirlist.reverse()

        folder=self
        path=""

        for dir in dirlist:
            if self.check_filename(path,dir):
                
                if dir in folder.objectIds():
                    if not folder[dir].isPrincipiaFolderish:
                        
                        raise RuntimeError,("Object '%s' already exists "+
                                            "and is no folder: Cannot "+
                                            "create or use folder") % dir
                else:
                    folder.manage_addFolder(id=dir)

                folder=folder[dir]

            else:
                return None # no folder, no files in there...

            if path:
                path=path + "/" + dir
            else:
                path=dir
                
        return folder
    
    
    
    def _edit_html(self, data):
        # a hook for filters to edit the imported html files
        return data

    def _add_other_file(self,folder,path,basename,sf):
        # Hook for other known file types, default: add file objects
        folder.manage_addFile(id=basename, title='', file=sf)


    def check_filename(self,pathname,basename):
        # return 0 to skip file, raise an exception to annoy...
        match=filenamepattern.match(basename) != None;
        if not match and basename != '':
            self._v_skipped.append(os.path.join(pathname,basename))
        return match



