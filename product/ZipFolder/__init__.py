from ZipFolder import *
from OFS import Folder

__doc__="""ZipFolder initialization module"""
__version__= '0.2'



def initialize(context):
    """Initialize the PaketFolder product"""

    
    context.registerClass(
        ZipFolder,
        constructors = (manage_addZipFolderForm,
                        manage_addZipFolder
                        ),
        icon='ZipFolder_icon.png'
        )
    
 
    context.registerHelp()
    
