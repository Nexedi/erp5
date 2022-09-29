# pylint: disable-all
from Products.PythonScripts.standard import html_quote
from Products.CMFCore.utils import getToolByName
from Products.FCKeditor.utils import fckCreateValidZopeId



# Author : jean-mat Grimaldi - jean-mat@macadames.com
# Thanks to Martin F. Krafft (alias madduck on sourceforge) for some corrections
# Thanks to kupu developpers for UID referencing
# This connector is plone specific
# Some functions need to be adapted for other Zope CMS compatibility

# 1. Config

# Path to user files relative to the document root.
# security tip
ConfigUserFilesPath=""

# dico fck parameters for browsing
fckParams=context.getFck_params()


# special review_states
# (unpublished states for contents which need to be hidden to local_roles
# not in fck prefs rolesSeeUnpublishedContent even with View permission )
unpublishedStates=fckParams['fck_unpublished_states']

# special local_roles who can see unpublished contents according to permissions
# by default set to fck unpublished view roles (fck prefs)
rolesSeeUnpublishedContent = fckParams['fck_unpublished_view_roles']

# PloneArticle based meta_types
pa_meta_types = fckParams['pa_meta_types']

# Allowed and denied extensions dictionaries

ConfigAllowedExtensions = {"File":None,
                           "Image":("jpg","gif","jpeg","png"),
                           "Flash":("swf","fla"),
                           "Media":("swf",
                                    "fla",
                                    "jpg",
                                    "gif",
                                    "jpeg",
                                    "png",
                                    "avi",
                                    "mpg",
                                    "mpeg",
                                    "mp1",
                                    "mp2",
                                    "mp3",
                                    "mp4",
                                    "wma",
                                    "wmv",
                                    "wav",
                                    "mid",
                                    "midi",
                                    "rmi",
                                    "rm",
                                    "ram",
                                    "rmvb",
                                    "mov",
                                    "qt")}
ConfigDeniedExtensions =  {"File":("py",
                                   "cpy",
                                   "pt",
                                   "cpt",
                                   "dtml",
                                   "php",
                                   "asp",
                                   "aspx",
                                   "ascx",
                                   "jsp",
                                   "cfm",
                                   "cfc",
                                   "pl",
                                   "bat",
                                   "exe",
                                   "com",
                                   "dll",
                                   "vbs",
                                   "js",
                                   "reg"),
                          "Image":None,
                          "Flash":None,
                          "Media":None}

# set link by UID for AT content Types
linkbyuid=test(fckParams['allow_link_byuid'],1,0)

# check if upload allowed for Links Image and internal links

allow_file_upload=test(fckParams['allow_server_browsing'],test(fckParams['allow_file_upload'],1,0),0)
allow_image_upload=test(fckParams['allow_server_browsing'],test(fckParams['allow_image_upload'],1,0),0)
allow_flash_upload=test(fckParams['allow_server_browsing'],test(fckParams['allow_flash_upload'],1,0),0)


# check for portal_types when uploading internal links, images and files

file_portal_type = test(fckParams['file_portal_type'],fckParams['file_portal_type'],'File')
image_portal_type = test(fckParams['image_portal_type'],fckParams['image_portal_type'],'Image')
flash_portal_type = test(fckParams['flash_portal_type'],fckParams['flash_portal_type'],'File')

# find Plone Site charset

try:
  prop   = getToolByName(context, "portal_properties")
  charsetSite = prop.site_properties.getProperty("default_charset", "utf-8")
except:
  charsetSite ="utf-8"


# 2. utils


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
  return utf8Encode(value).replace("\"", "&quot;").replace("'","&rsquo;").replace("&", "&amp;")




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
    header.append('\r    <CurrentFolder path="%s" url="%s/" />'\
                   % (ConvertToXmlAttribute(currentFolder),
                      ConvertToXmlAttribute(GetUrlFromPath(currentFolder))))
    return ''.join(header)


def CreateXmlFooter():
    return '\r</Connector>'



def xmlString(results, resourceType, foldersOnly, isPA):

    user=context.REQUEST['AUTHENTICATED_USER']
    # traitement xml
    xmlFiles=['\r        <Files>']
    xmlFolders=['\r        <Folders>']


    # traitement folderish standard non PloneArticle
    if isPA ==0:
        for result in results :
            titre = result.title_or_id()
            if linkbyuid and hasattr(result.aq_explicit, 'UID'):
               tagLinkbyuid="yes"
               uid = result.UID()
            else :
               tagLinkbyuid="no"
               uid=""
            if result.isPrincipiaFolderish or result.meta_type in pa_meta_types :
                xmlFolders.append('''
            <Folder name="%s"
                    title="%s"
                    linkbyuid="%s"
                    uid="%s"
                    type="%s"
                    metatype="%s" />'''%(ConvertToXmlAttribute(result.getId()),
                                         ConvertToXmlAttribute(titre),
                                         tagLinkbyuid, uid,
                                         resourceType,
                                         ConvertToXmlAttribute(result.meta_type)))
            else :
                if result.meta_type in ('CMF ZPhoto', 'CMF Photo'):
                   tagPhoto="yes"
                else:
                   tagPhoto= "no"
                isAttach = "no"
                attachId=""
                xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPA3img="no"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(result.getId()),
                                       str(context.getObjSize(result)),
                                       ConvertToXmlAttribute(titre),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       attachId))
    # PloneArticle specific treatment
    elif user.has_permission('View', results) :
        # find Plone Article version and brains for PA v3
        try :
            image_brains =results.getImageBrains()
            attachment_brains=results.getAttachmentBrains()
            versionPA=3
        except:
            versionPA=2

        # Plone Article v3 treatment
        if versionPA==3:
            atool = context.portal_article
            #  PloneArticle 3.x images and attachements
            # images
            for image_brain in image_brains :
                image = image_brain.getObject()
                image_field = image.getField('image')
                image_name = atool.getFieldFilename(image, image_field)
                image_id = image.getId()
                image_title = image.title_or_id()
                image_size = context.plonearticle_format_size(image.get_size())
                tagPhoto= "no"
                isAttach = "no"
                if linkbyuid and hasattr(image.aq_explicit, 'UID'):
                    tagLinkbyuid="yes"
                    uid = image.UID()
                else:
                    tagLinkbyuid="no"
                    uid=""
                xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPA3img="yes"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(image_id),
                                       image_size,
                                       ConvertToXmlAttribute(image_title),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       ConvertToXmlAttribute(image_name)))

            # files and other resource types
            if resourceType!='Image':
                for attach_brain in attachment_brains :
                    attach = attach_brain.getObject()
                    attach_field = attach.getField('file')
                    attach_name = atool.getFieldFilename(attach, attach_field)
                    attach_id = attach.getId()
                    attach_title = attach.title_or_id()
                    attach_size = context.plonearticle_format_size(attach.get_size())
                    tagPhoto= "no"
                    isAttach = "no"
                    if linkbyuid and hasattr(attach.aq_explicit, 'UID'):
                        tagLinkbyuid="yes"
                        uid = attach.UID()
                    else:
                        tagLinkbyuid="no"
                        uid=""
                    xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPA3img="no"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(attach_id),
                                       attach_size,
                                       ConvertToXmlAttribute(attach_title),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       ConvertToXmlAttribute(attach_name)))


        # PloneArticle v2.x
        else:
            tagLinkbyuid="no"
            uid=""
            # images
            if len(results.listImages())>0:
                images = results.listImages()
                index=0
                for image in images :
                    titre = image.title_or_id()
                    # get Id
                    imageId=results.getImageId(index)
                    index +=1
                    # get Size object
                    try:
                        imageSize=image.getSize()
                    except:
                        imageSize=context.getObjSize(image)
                    tagPhoto= "no"
                    isAttach = "no"
                    attachId = image.getId()
                    xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPA3img="no"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(imageId),
                                       imageSize,
                                       ConvertToXmlAttribute(titre),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       ConvertToXmlAttribute(attachId)))

            # files and other ressources types
            if len(results.listAttachments())>0 and resourceType!='Image':
                attachements = results.listAttachments()
                index=0
                for attachement in attachements :
                    titre = attachement.title_or_id()
                    # get Id
                    attachementId=results.getAttachmentId(index)
                    index +=1
                    # get Size object
                    try:
                        attachementSize=attachement.getSize()
                    except:
                        attachementSize=context.getObjSize(attachement)
                    tagPhoto= "no"
                    isAttach = "yes"
                    attachId=attachement.getFilename()
                    xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPA3img="no"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(attachementId),
                                       attachementSize,
                                       ConvertToXmlAttribute(titre),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       ConvertToXmlAttribute(attachId)))



    xmlFiles.append('\r        </Files>')
    xmlFolders.append('\r        </Folders>')
    if foldersOnly:
        stringXml=''.join(xmlFolders)
    else :
        stringXml=''.join(xmlFolders)+''.join(xmlFiles)
    return stringXml


def CreateXmlErrorNode (errorNumber,errorDescription):

    return '''
        <Error number="%s"
               originalNumber="%s"
               originalDescription="%s" />'''%(errorNumber,
                                               errorNumber,
                                               ConvertToXmlAttribute(errorDescription))


# 5. commands
# Specific Plone - for others CMS (CPS ...), for special folderish (Plone Article, doc flexible ...) change these lines

def GetFoldersAndFiles( resourceType, currentFolder ):
    results=[]
    user=context.REQUEST['AUTHENTICATED_USER']
    if currentFolder != "/" :
        obj = context.restrictedTraverse(currentFolder.lstrip('/'))
    else :
        obj = context.portal_url.getPortalObject()
    # objet folderish
    if obj.meta_type not in pa_meta_types:
        types=context.portal_types
        all_portal_types = [ctype.content_meta_type for ctype in types.objectValues()]
        if resourceType=="Image" :
          accepted_types=[ctype.content_meta_type for ctype in types.objectValues() if ctype.id in (image_portal_type, 'Photo', 'ZPhoto')]
        elif resourceType=="Flash" :
          accepted_types=[ctype.content_meta_type for ctype in types.objectValues() if ctype.id == flash_portal_type ]
        else :
          accepted_types = all_portal_types
        for object in obj.objectValues():
          if object.meta_type in accepted_types or (object.meta_type in all_portal_types  and (object.isPrincipiaFolderish or object.meta_type in pa_meta_types)) :
            review_state=container.portal_workflow.getInfoFor(object, 'review_state', '')
            start_pub=getattr(object,'effective_date',None)
            end_pub=getattr(object,'expiration_date',None)
            if review_state not in unpublishedStates and not ((start_pub and start_pub > DateTime()) or (end_pub and DateTime() > end_pub)):
              results.append(object)
            elif user.has_role(rolesSeeUnpublishedContent,object) :
              results.append(object)
        results = [ s for s in results if user.has_permission('View', s) ]
        return xmlString(results,resourceType,0,0)

    # objet Plone article find attachements and images
    else:
        # oblige d'envoyer l'objet car trop specifique
        return xmlString(obj,resourceType,0,1)



def GetFolders( resourceType, currentFolder ):
    results=[]
    user=context.REQUEST['AUTHENTICATED_USER']
    types=context.portal_types
    all_portal_types = [ctype.content_meta_type for ctype in types.objectValues()]
    if currentFolder != "/" :
        obj = context.restrictedTraverse(currentFolder.lstrip('/'))
    else :
        obj = context.portal_url.getPortalObject()
    for object in obj.objectValues():
      if object.meta_type in all_portal_types and (object.isPrincipiaFolderish or object.meta_type=='PloneArticle') :
        review_state=container.portal_workflow.getInfoFor(object, 'review_state', '')
        start_pub=getattr(object,'effective_date',None)
        end_pub=getattr(object,'expiration_date',None)
        if review_state not in unpublishedStates and not ((start_pub and start_pub > DateTime()) or (end_pub and DateTime() > end_pub)):
          results.append(object)
        elif user.has_role(rolesSeeUnpublishedContent,object) :
          results.append(object)
    results = [ s for s in results if user.has_permission('View', s) ]
    return xmlString(results,resourceType,1,0)


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

    if obj.meta_type == 'PloneArticle':
       sErrorNumber = "103"
       sErrorDescription = "folder creation forbidden"

    if not folderName:
       sErrorNumber = "102"
       sErrorDescription = "invalid folder name"

    if not sErrorNumber :
      try :
        folderTitle=utf8Decode(folderName)
        folderName = fckCreateValidZopeId(utf8Encode(folderTitle))
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

        if obj.meta_type != 'PloneArticle':
            # define Portal Type to add

            if resourceType == 'File':
                typeToAdd = file_portal_type
            elif resourceType == 'Flash':
                typeToAdd = flash_portal_type
            elif resourceType == 'Image' :
                if obj.meta_type=="CMF ZPhotoSlides":
                    typeToAdd = 'ZPhoto'
                elif obj.meta_type=="Photo Album":
                    typeToAdd = 'Photo'
                elif obj.meta_type=="ATPhotoAlbum":
                    typeToAdd = 'ATPhoto'
                else:
                    typeToAdd = image_portal_type


            if not user.has_permission('Add portal content', obj) and not user.has_permission('Modify portal content', obj):
               error = "103"

            if resourceType == 'Image' and not allow_image_upload:
               error = "103"

            if resourceType == 'Flash' and not allow_flash_upload:
               error = "103"

            if resourceType not in ('Flash','Image') and not allow_file_upload:
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
                    obj.invokeFactory(id=idObj, type_name=typeToAdd, title=titre_data )
                    newFile = getattr(obj, idObj)
                    newFile.edit(file=data)
                    obj.reindexObject()

                except:
                    error = "103"

        #Plone Article treatment
        else :
            # find Plone Article version
            try :
                image_brains = obj.getImageBrains()
                attachment_brains = obj.getAttachmentBrains()
                versionPA=3
            except:
                versionPA=2

            if not data:
                #pas de fichier
                error= "1"
                customMsg="no file uploaded"
            else :
                filename=utf8Decode(getattr(data,'filename', ''))
                titre_data=filename[max(string.rfind(filename, '/'),
                                string.rfind(filename, '\\'),
                                string.rfind(filename, ':'),
                                )+1:]

                # idObj can't be cleaned with PloneArticle attachements
                # it's a problem but we do the job
                idObj=fckCreateValidZopeId(utf8Encode(titre_data))
                if title :
                    titre_data=title

                if resourceType == 'Image' :
                    # Upload file
                    if not user.has_permission('Modify portal content', obj):
                        error = "103"
                    elif not allow_image_upload:
                        error = "103"
                    elif not IsAllowedExt( FindExtension(idObj), resourceType ):
                        error= "202"
                        customMsg="Invalid file type"
                    elif obj.portal_article.checkImageSize(data):
                        if versionPA==2 :
                            obj.appendImage(titre_data, data, )
                        else :
                            obj.addImage(title=titre_data, description='', image=data)
                        error="0"
                        try:
                            obj.reindexObject()
                        except:
                            parent = obj.aq_parent
                            parent.reindexObject()

                    else:
                        error="104"
                else:
                    # Upload file
                    if not user.has_permission('Modify portal content', obj):
                        error = "103"
                    elif not allow_file_upload:
                        error = "103"
                    elif not IsAllowedExt( FindExtension(idObj), resourceType ):
                        error= "202"
                        customMsg="Invalid file type"
                    elif obj.portal_article.checkAttachmentSize(data):
                        if versionPA==2 :
                            obj.appendAttachment(titre_data, data, )
                        else :
                            obj.addAttachment(title=titre_data, description='', file=data)
                        error="0"
                        try:
                            obj.reindexObject()
                        except:
                            parent = obj.aq_parent
                            parent.reindexObject()
                    else:
                        error="104"


        d= '''
        <script type="text/javascript">
        window.parent.frames['frmUpload'].OnUploadCompleted(%s,"%s") ;
        </script>
        '''% (error,idObj)
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

        RESPONSE.setHeader('Cache-control','pre-check=0,post-check=0,must-revalidate,s-maxage=0,max-age=0,no-cache')
        RESPONSE.setHeader('Content-type', 'text/xml; charset=utf-8')
        xmlHeader = CreateXmlHeader (sCommand, sResourceType, sCurrentFolder)

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
