
import os
import string
import tempfile
import types

import StringIO
import zipfile


MINZIPFILESIZE=22


class ZipImporter:
    """A mix-in class to add zipfile-import-support to folders"""


    def import_zipfile(self,file):
        
        # minimum/maximum size check
        file.seek(0,2)
        fsize=file.tell()
        file.seek(0,0)
        if fsize > self.max_zipfile_size():
            raise RuntimeError,'ZIP file is too big'

        if fsize < MINZIPFILESIZE:
            raise RuntimeError,'ZIP file is too small'

        zf=zipfile.ZipFile(file,'r')

        try:
            self.check_zip(zf)
                
            for name in zf.namelist():
                self._add_file_from_zip(zf,name)
                    
        finally:
            zf.close()


    def _add_file_from_zip(self,zipfile,name):

        basename=os.path.basename(name)
        pathname=os.path.dirname(name)
        if not self.check_filename(pathname,basename):
            return # skip ugly files
        
        sf=StringIO.StringIO(zipfile.read(name))
        self.add_file(pathname,basename,sf)
        sf.close()


    #
    #
    # To be overwritten:
     
    def max_zipfile_size(self):
        """return maximum size for zip files. Default 4MB"""
        return 4*1024*1024;
    

    def check_zip(self,zipfile):
        # a hook to check zipfile before import loop
        # maybe: Look for a special file in the zip...
        
        pass

    
    def check_filename(self,pathname,basename):
        # return 0 to skip file, raise an exception to annoy...
        return 1;

    def add_file(self,pathname,basename,file):
        #add file to whatever...
        #is called with path,basename and file handle

        # overwrite this!
        pass
    
    

