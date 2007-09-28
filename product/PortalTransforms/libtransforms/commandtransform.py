import os
import sys
import tempfile
import re
import shutil
from os.path import join, basename

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext, getShortPathName

class commandtransform:
    """abstract class for external command based transform
    """
    __implements__ = itransform

    def __init__(self, name=None, binary=None, **kwargs):
        if name is not None:
            self.__name__ = name
        if binary is not None:
            self.binary = bin_search(binary)
            self.binary = getShortPathName(self.binary)

    def name(self):
        return self.__name__

    def initialize_tmpdir(self, data, **kwargs):
        """create a temporary directory, copy input in a file there
        return the path of the tmp dir and of the input file
        """
        tmpdir = tempfile.mktemp()
        os.mkdir(tmpdir)
        filename = kwargs.get("filename", '')
        fullname = join(tmpdir, basename(filename))
        filedest = open(fullname , "wb").write(data)
        return tmpdir, fullname

    def subObjects(self, tmpdir):
        imgs = []
        for f in os.listdir(tmpdir):
            result = re.match("^.+\.(?P<ext>.+)$", f)
            if result is not None:
                ext = result.group('ext')
                if ext in ('png', 'jpg', 'gif'):
                    imgs.append(f)
        path = join(tmpdir, '')
        return path, imgs

    def fixImages(self, path, images, objects):
        for image in images:
            objects[image] = open(join(path, image), 'rb').read()

    def cleanDir(self, tmpdir):
        shutil.rmtree(tmpdir)

class popentransform:
    """abstract class for external command based transform

    Command must read from stdin and write to stdout
    """
    __implements__ = itransform

    binaryName = ""
    binaryArgs = ""
    useStdin = True

    def __init__(self, name=None, binary=None, binaryArgs=None, useStdin=None,
                 **kwargs):
        if name is not None:
            self.__name__ = name
        if binary is not None:
            self.binary = bin_search(binary)
        else:
            self.binary = bin_search(self.binaryName)
        if binaryArgs is not None:
            self.binaryArgs = binaryArgs
        if useStdin is not None:
            self.useStdin = useStdin

    def name(self):
        return self.__name__

    def getData(self, couterr):
        return couterr.read()

    def convert(self, data, cache, **kwargs):
        command = "%s %s" % (self.binary, self.binaryArgs)
        if not self.useStdin:
            tmpfile, tmpname = tempfile.mkstemp(text=False) # create tmp
            os.write(tmpfile, data) # write data to tmp using a file descriptor
            os.close(tmpfile)       # close it so the other process can read it
            command = command % { 'infile' : tmpname } # apply tmp name to command

        cin, couterr = os.popen4(command, 'b')

        if self.useStdin:
            cin.write(str(data))

        status = cin.close()

        out = self.getData(couterr)
        couterr.close()

        if not self.useStdin:
            # remove tmp file
            os.unlink(tmpname)

        cache.setData(out)
        return cache
