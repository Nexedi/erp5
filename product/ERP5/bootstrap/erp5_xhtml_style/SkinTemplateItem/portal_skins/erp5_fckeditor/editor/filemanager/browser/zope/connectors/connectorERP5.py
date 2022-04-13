# pylint: disable-all
from Products.PythonScripts.standard import html_quote
from Products.CMFCore.utils import getToolByName


#############
# This connector is based on CPS connector from the FCKeditor/zope integration product
#############

# 1. Config

# Path to user files relative to the document root.
ConfigUserFilesPath=""
# SECURITY TIP: Uncomment the following line to set a fixed path
# ConfigUserFilesPath = "/UserFiles/"
# SECURITY TIP: Uncomment the 3 following code lines to force the Plone Member Home Folder as fixed path
# You can do it as well with wysiwyg_support templates customization
# it's just more secure
# portal=context.portal_url.getPortalObject()
# portal_url=portal.absolute_url()
# ConfigUserFilesPath = portal.portal_membership.getHomeUrl().replace(portal_url, '') + '/'

# special review_states
# (unpublished states for contents which need to be hidden to local_roles
# not in rolesSeeUnpublishedContent even with View permission )
unpublishedStates = []   #['visible','pending','rejected', 'waitreview']

# special local_roles who can see unpublished contents according to permissions
# by default set to None
rolesSeeUnpublishedContent = None
# you can force the value here
# rolesSeeUnpublishedContent = ['Manager','Reviewer','Owner', 'Contributor']

# if rolesSeeUnpublishedContent is None we try to take it from portal_properties > navtree_properties
if not rolesSeeUnpublishedContent:
  try:
    props=getToolByName(context,'portal_properties')
    if hasattr(props,'navtree_properties'):
        props=props.navtree_properties
    rolesSeeUnpublishedContent=getattr(props,'rolesSeeUnpublishedContent',  ['Manager','Reviewer','Owner'])
  except:
    rolesSeeUnpublishedContent = ['Manager','Reviewer','Owner']

# Allowed and denied extensions dictionaries

ConfigAllowedExtensions = { "File" : None
                          , "Image": ( "jpg", "gif", "jpeg", "png")
                          , "Flash": ( "swf", "fla")
                          , "Media": ( "swf", "fla"
                                     , "jpg", "gif", "jpeg", "png"
                                     , "avi"
                                     , "mpg", "mpeg", "mp1", "mp2", "mp3", "mp4"
                                     , "wma", "wmv"
                                     , "wav", "mid", "midi"
                                     , "rmi", "rm", "ram", "rmvb"
                                     , "mov", "qt"
                                     )
                          }
ConfigDeniedExtensions = { "Image": None
                         , "Flash": None
                         , "Media": None
                         , "File" : ( "py", "cpy"
                                    , "pt", "cpt", "dtml"
                                    , "php"
                                    , "asp", "aspx", "ascx"
                                    , "jsp"
                                    , "cfm", "cfc"
                                    , "pl"
                                    , "bat", "exe", "com", "dll"
                                    , "vbs"
                                    , "js"
                                    , "reg"
                                    )
                          }

# link by uid is against ERP5 rules
linkbyuid = 0

ERP5_FOLDER_TYPE = ['Folder', 'ERP5 Folder', 'ERP5 Document', ' ERP5 Web Page']

# ERP5 is full UTF-8, no need to get charset dynamiccaly
charsetSite = "utf-8"


# 2. utils

def RemoveFromStart(sourceString,charToRemove ):
  return sourceString.lstrip(charToRemove)

def utf8Encode(chaine) :

    errors="strict"
    if charsetSite.lower() in ("utf-8", "utf8"):
      return chaine
    else:
      return unicode(chaine, charsetSite, errors).encode("utf-8", errors)

def utf8Decode(chaine) :
    # because browser upload form is in utf-8 we need it
    errors="strict"
    if charsetSite.lower() in ("utf-8", "utf8"):
        return chaine
    else:
        try:
            chaine = unicode(chaine, "utf-8", "strict").encode(charsetSite, "strict")
        except:
            chaine = chaine.encode(charsetSite, "strict")
        return chaine

def ConvertToXmlAttribute( value ):
  return utf8Encode(value).replace("\"", "&quot;").replace("&", "&amp;")

def fckCreateValidZopeId(s):
    """
    Return a valid Zope id from the given string
    """
    id = s.decode('utf-8')
    # we cannot access unicodedata.normalize in restricted environment.
    # id = unicodedata.normalize('NFKD', id)
    id = id.encode('ascii', 'ignore')

    # remove invalid ascii chars for ids
    new_id = ''
    for a in id:
        if a in string.digits or a in string.lowercase or a in string.uppercase or a=='.' or a==' ' or a=='-' or a=='_':
            new_id += a
    new_id = new_id.replace(' ','-')
    new_id = new_id.replace('_','-')
    new_id = '-'.join([e for e in new_id.split('-') if e])
    # ids in lower case
    return new_id.lower()



# 3. io



def GetUrlFromPath( folderPath ) :

    return '%s%s' %(portal_path,folderPath.rstrip("/"))


def RemoveExtension( fileName ):

   sprout=fileName.split(".")
   return '.'.join(sprout[:len(sprout)-1])

def  IsAllowedExt( extension, resourceType ) :

   sAllowed = ConfigAllowedExtensions[resourceType]
   sDenied = ConfigDeniedExtensions[resourceType]

   if (sAllowed is None or extension in sAllowed) and (sDenied is None or extension not in sDenied) :
     return 1
   else :
     return 0

def FindExtension (fileName):

   sprout=fileName.split(RemoveExtension(fileName))
   return ''.join(sprout).lstrip('.')





# 4. basexml

def CreateXmlHeader( command, resourceType, currentFolder ):
    header = ['<?xml version="1.0" encoding="utf-8" ?>']
    header.append('\r<Connector command="%s" resourceType=" %s ">'% (command,resourceType))
    header.append('\r    <CurrentFolder path="%s" url="%s/" />'% (ConvertToXmlAttribute(currentFolder),ConvertToXmlAttribute(GetUrlFromPath(currentFolder))))
    return ''.join(header)


def CreateXmlFooter():
    return '\r</Connector>'



def xmlString(results, resourceType, foldersOnly):

    # traitement xml
    xmlFiles=['\r        <Files>']
    xmlFolders=['\r        <Folders>']

    for result in results :

        titre = result.title_or_id()
        # create a safe title string
        titre = titre.replace("'", "-")
        titre = titre.replace('"', "-")

        if linkbyuid and hasattr(result, 'uid'):
           tagLinkbyuid="yes"
           uid = result.getUid()
        else :
           tagLinkbyuid="no"
           uid=""

        if result.meta_type in ERP5_FOLDER_TYPE :

            try:
               xmlFolders.append('\r            <Folder name="%s" title="%s" linkbyuid="%s" uid="%s" type="%s" metatype="%s" />'%(ConvertToXmlAttribute(result.id),ConvertToXmlAttribute(titre), tagLinkbyuid, uid, resourceType, ConvertToXmlAttribute(result.meta_type)))

            except Exception as e:
               pass

        else :
            tagPhoto= "no"
            size='unknown size'
            unit=''
            try:
               size = result.get_size()
               if size >= (1024*1024):
                 size = size / (1024*1024)
                 unit = " MB"
               elif size >= 1024:
                 size = size / 1024
                 unit = " KB"
               else:
                 unit = " Bytes"
            except Exception as e:
               pass
            try:
               xmlFiles.append('\r            <File name="%s" size="%s%s" title="%s" photo="%s" linkbyuid="%s" uid="%s" type="%s" isPA3img="no" isattach="no" attachid="" />'%(ConvertToXmlAttribute(result.getId()),size,unit,ConvertToXmlAttribute(titre), tagPhoto, tagLinkbyuid, uid, resourceType))

            except Exception as e:
               pass

    xmlFiles.append('\r        </Files>')
    xmlFolders.append('\r        </Folders>')

    if foldersOnly:
        stringXml=''.join(xmlFolders)
    else:
        stringXml=''.join(xmlFolders)+''.join(xmlFiles)
    return stringXml


def CreateXmlErrorNode (errorNumber,errorDescription):

    return '\r        <Error number="' + errorNumber + '" originalNumber="' + errorNumber + '" originalDescription="' + ConvertToXmlAttribute( errorDescription ) + '" />'


# 5. commands

def GetFoldersAndFiles( resourceType, currentFolder ):
    results=[]
    user=context.REQUEST['AUTHENTICATED_USER']
    types=context.portal_types

    if resourceType=="Image" :
      accepted_types=[ctype.id for ctype in types.objectValues() if ctype.id in ('Image', )]



    elif resourceType=="Flash":
      accepted_types=[ctype.id for ctype in types.objectValues() if ctype.id in ('Flash Animation', )]

    #elif resourceType not in ('Image', 'Flash') :
    #  accepted_types=[ctype.id for ctype in types.objectValues()]

    else :
      accepted_types = [ctype.id for ctype in types.objectValues()]
    if currentFolder != "/" :
      try:
        obj = context.restrictedTraverse(currentFolder.lstrip('/'))
      except Exception as e:

        obj = context.portal_url.getPortalObject()
    else :

      obj = context.portal_url.getPortalObject()


    for object in obj.objectValues():
      mtool = context.portal_membership
      checkPerm = mtool.checkPermission

      if not checkPerm('View', object):
        pass


      if object.portal_type in accepted_types or (object.meta_type in ERP5_FOLDER_TYPE) :

        results.append(object)

    results = [ s for s in results if user.has_permission('View', s) ]

    return xmlString(results,resourceType,0)


def GetFolders( resourceType, currentFolder ):
    results=[]
    user=context.REQUEST['AUTHENTICATED_USER']
    types=context.portal_types

    if currentFolder != "/" :

        #try:

        obj = context.restrictedTraverse(currentFolder.lstrip('/'))
        #except Exception,e:

        #   obj = context.portal_url.getPortalObject()

    else :
        #obj = context.portal_url.getPortalObject()
        return xmlString([],resourceType,1)


    mtool = context.portal_membership
    checkPerm = mtool.checkPermission

    for object in obj.objectValues():


      # filter out objects that cannot be viewed
      if not user.has_permission('View', object):

        continue


      try:
        if object.meta_type in ERP5_FOLDER_TYPE:

          #review_state=container.portal_workflow.getInfoFor(object, 'review_state', '')
          start_pub=getattr(object,'effective_date',None)
          end_pub=getattr(object,'expiration_date',None)
          if not ((start_pub and start_pub > DateTime()) or (end_pub and DateTime() > end_pub)):
            results.append(object)
          elif user.has_role(rolesSeeUnpublishedContent,object) :
            results.append(object)
      except Exception as e:
          pass
    results = [ s for s in results if user.has_permission('View', s) ]

    return xmlString(results,resourceType,1)


def CreateFolder(currentFolder, folderName ):

    user=context.REQUEST['AUTHENTICATED_USER']
    if currentFolder != "/" :
        obj = context.restrictedTraverse(currentFolder.lstrip('/'))
    else :
        obj = context.portal_url.getPortalObject()
    sErrorNumber=""

    # error cases
    if not user.has_permission('Add portal content', obj) and not user.has_permission('Modify portal content', obj):
       sErrorNumber = "103"
       sErrorDescription = "folder creation forbidden"

    if not folderName:
       sErrorNumber = "102"
       sErrorDescription = "invalid folder name"

    if not sErrorNumber :
      try :
        folderTitle=utf8Decode(folderName)
        folderName = fckCreateValidZopeId(utf8Encode(folderName))
        new_id = obj.invokeFactory(id=folderName, type_name='Folder', title=folderTitle)
        sErrorNumber = "0"
        sErrorDescription = "success"
      except :
        sErrorNumber = "103"
        sErrorDescription = "folder creation forbidden"

    return CreateXmlErrorNode(sErrorNumber,sErrorDescription)




# 6. upload

def UploadFile(resourceType, currentFolder, data, title) :

        user=context.REQUEST['AUTHENTICATED_USER']
        if currentFolder != "/" :
            obj = context.restrictedTraverse(currentFolder.lstrip('/'))
        else :
            obj = context.portal_url.getPortalObject()
        error=""
        idObj=""

        # define Portal Type to add
        if resourceType == 'Image' :
            typeToAdd='Image'
        else:
            typeToAdd = 'File'



        if not user.has_permission('Add portal content', obj) and not user.has_permission('Modify portal content', obj):
           error = "103"

        if not data:
          #pas de fichier
          error= "202"

        titre_data=''
        filename=utf8Decode(getattr(data,'filename', ''))
        titre_data=filename[max(string.rfind(filename, '/'),
                        string.rfind(filename, '\\'),
                        string.rfind(filename, ':'),
                        )+1:]

        idObj=fckCreateValidZopeId(utf8Encode(titre_data))
        context.log('xxx', idObj)



        if title :
           titre_data=title

        if not IsAllowedExt( FindExtension(idObj), resourceType ):
              error= "202"

        if not error :
            error="0"
            indice=0
            exemple_titre=idObj
            while exemple_titre in obj.objectIds():
              indice=indice+1
              exemple_titre=str(indice) + idObj
            if indice!=0:
                error= "201"
                idObj = exemple_titre

            try:
                # this method need to be changed for browser refresh
                # because it send 302 redirection : we need no http response
                new_image = obj.newContent(portal_type=typeToAdd, id=idObj, title=titre_data, file=data)
                new_image.reindexObject()

            except Exception as e :
                error = "103"

        d= '''
        <script type="text/javascript">
        window.parent.frames['frmUpload'].OnUploadCompleted(%s,"%s") ;
        </script>
        '''% (error, idObj)


        return d


#7. connector


request = context.REQUEST
RESPONSE =  request.RESPONSE
dicoRequest = request.form
message_error=""

portal_url=context.portal_url.getPortalObject().absolute_url()
server_url = request.SERVER_URL
portal_path = portal_url.replace(server_url,'')

if ConfigUserFilesPath != "" :
   sUserFilesPath = ConfigUserFilesPath
elif 'ServerPath' in dicoRequest:
   sUserFilesPath = dicoRequest ['ServerPath']
else :
   sUserFilesPath = "/"


if 'CurrentFolder' in dicoRequest:
   sCurrentFolder = dicoRequest ['CurrentFolder']
   if sUserFilesPath!='/' and sUserFilesPath.rstrip('/') not in sCurrentFolder:
        sCurrentFolder = sUserFilesPath
else :
   message_error="No CurrentFolder in request"



if 'Command' in dicoRequest:
    sCommand = dicoRequest ['Command']
else :
    message_error="No Command in request"

if 'Type' in dicoRequest:
    sResourceType = dicoRequest ['Type']
else :
    message_error="No Type in request"


if 'NewFolderName' in dicoRequest:
    sFolderName = dicoRequest ['NewFolderName']


# interception File Upload
if sCommand=='FileUpload' and 'NewFile' in dicoRequest:
    sData = dicoRequest ['NewFile']
    sTitle = utf8Decode(dicoRequest ['Title'])
    chaineHtmlUpload = UploadFile(sResourceType, sCurrentFolder, sData, sTitle)
    RESPONSE.setHeader('Content-type', 'text/html; charset=%s' % charsetSite)
    return chaineHtmlUpload


else :

    # Creation response XML
    if not message_error :

        RESPONSE.setHeader('Cache-control', 'pre-check=0,post-check=0,must-revalidate,s-maxage=0,max-age=0,no-cache')
        RESPONSE.setHeader('Content-type', 'text/xml; charset=utf-8')

        xmlHeader = CreateXmlHeader (sCommand, sResourceType, sCurrentFolder)

        xmlBody = ''
        if sCommand=="GetFolders":
            xmlBody = GetFolders (sResourceType, sCurrentFolder)
        elif sCommand=="GetFoldersAndFiles":
            xmlBody = GetFoldersAndFiles (sResourceType, sCurrentFolder)
        elif sCommand=="CreateFolder":
            xmlBody = CreateFolder (sCurrentFolder,sFolderName)

        xmlFooter = CreateXmlFooter()
        return xmlHeader + xmlBody + xmlFooter

    # creation response error request
    else :

        sErrorNumber="218"
        sErrorDescription="Browser Request exception : " + message_error
        xmlHeader = CreateXmlHeader (sCommand, sResourceType, sCurrentFolder)
        xmlFooter = CreateXmlFooter()
        return xmlHeader + CreateXmlErrorNode(sErrorNumber,sErrorDescription) + xmlFooter
