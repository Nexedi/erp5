var oListManager = new Object() ;
// define the nb cell by row for album presentation
var nbCell=3;

oListManager.Init = function()
{
	this.Table = document.getElementById('tableFiles') ;
}

oListManager.Clear = function()
{
	// Remove all other rows available.
	while ( this.Table.rows.length > 0 )
		this.Table.deleteRow(0) ;
}

oListManager.AddFolder = function( folderName, folderTitle, folderPath, sType, sLinkbyuid, sUid )
{
	// Create the new row.
	var oRow = this.Table.insertRow(-1) ;

	// Build the link to view the folder.
	var sLink = '<a href="#" onclick="OpenFolder(\'' + folderPath + '\');return false;">' ;
        var sLinkFolder = '';
        if (sType!='Image') {
                            if (sLinkbyuid=='yes' && sUid !='') {
                                                                 sFolderUrl = './resolveUid/' + sUid ;
                                                                }
                            else                                {
                                                                 sFolderUrl = folderPath ;
                                                                }
                            sLinkFolder = '<a title="link the folder" href="#" onclick="OpenFile(\'' + sFolderUrl + '\');return false;"><img alt="link the folder" src="images/lier.gif" width="12" height="12" border="0"><\/a>' ;
                            }

	// Add the folder icon cell.
	var oCell = oRow.insertCell(-1) ;
	oCell.width = 16 ;
	oCell.innerHTML = sLink + '<img alt="" src="images/Folder.gif" width="16" height="16" border="0"><\/a>' ;

	// Add the folder name cell.
	oCell = oRow.insertCell(-1) ;
	oCell.noWrap = true ;
	oCell.colSpan = 2 ;
	oCell.innerHTML = '&nbsp;' + sLink + folderTitle + '<\/a>&nbsp;' + sLinkFolder  ;
}

oListManager.AddFile = function( fileName, fileTitle, filePhoto, fileUrl, fileSize, sType )
{
	// Create the new row.
	var oRow = this.Table.insertRow(-1) ;

	// Build the link to view the file.
        var sLink = '<a href="#" onclick="OpenFile(\'' + fileUrl + '\');return false;">' ;
        // Change the link if type is image since setUrl for images support more arguments
        if (sType=='Image') {
	                        sLink = '<a href="#" onclick="OpenImage(\'' + fileUrl + '\',\'\',\'\',\'' + fileTitle + '\');return false;">' ;
                               }

	// Get the file icon.
	var sIcon = oIcons.GetIcon( fileName ) ;

	// Add the file icon cell.
	var oCell = oRow.insertCell(-1) ;
	oCell.width = 16 ;
	oCell.innerHTML = sLink + '<img alt="" src="images/icons/' + sIcon + '.gif" width="16" height="16" border="0"><\/a>' ;

	// Add the file name cell.
	oCell = oRow.insertCell(-1) ;
	oCell.innerHTML = '&nbsp;' + sLink + fileTitle + '<\/a>' ;
        if (filePhoto=='yes') {
                               var sLinkThumb = '<a href="#" onclick="OpenImage(\'' + fileUrl + '?size=thumb\',\'\',\'\',\'' + fileTitle + '\');return false;">' ;
                               var sLinkMedium = '<a href="#" onclick="OpenImage(\'' + fileUrl + '?size=medium\',\'\',\'\',\'' + fileTitle + '\');return false;">' ;
                               var sLinkFull = '<a href="#" onclick="OpenImage(\'' + fileUrl + '?size=full\',\'\',\'\',\'' + fileTitle + '\');return false;">' ;
                               // Add the photo cell.
                               oCell = oRow.insertCell(-1) ;
                               oCell.innerHTML = 'Photo&nbsp;Size&nbsp;:&nbsp;' + sLinkThumb + 'small<\/a>&nbsp;-&nbsp;' + sLinkMedium + 'medium<\/a>&nbsp;-&nbsp;' + sLinkFull + 'full<\/a>' ;
                              }
	
	// Add the file size cell.
	oCell = oRow.insertCell(-1) ;
	oCell.noWrap = true ;
	oCell.align = 'right' ;
	oCell.innerHTML = '&nbsp;' + fileSize + ' KB' ;
}

oListManager.AddFolderToAlbum = function( folderName, folderTitle, folderPath, sType, sLinkbyuid, sUid, numCell )
{

      
	// Create the new row.
        if (numCell%nbCell==0)
        {
	    var oRow = this.Table.insertRow(-1) ;
        }
        else
        {
            numRow = Math.floor (numCell/nbCell);
            var oRow= this.Table[numCell];
        }

	// Build the link to view the folder.
	var sLink = '<a href="#" title="browse the folder" onclick="OpenFolder(\'' + folderPath + '\');return false;">' ;
        var sLinkFolder = '&nbsp;';
        if (sType!='Image') {
                            if (sLinkbyuid=='yes' && sUid !='') {
                                                                 sFolderUrl = './resolveUid/' + sUid ;
                                                                }
                            else                                {
                                                                 sFolderUrl = folderPath ;
                                                                }
                            sLinkFolder = '<a title="link the folder" href="#" onclick="OpenFile(\'' + sFolderUrl + '\');return false;"><img alt="link the folder" src="images/lier.gif" width="12" height="12" border="0">&nbsp;Link the folder<\/a>' ;
                            }

	// Add the folder icon cell.
	var oCell = oRow.insertCell(-1) ;
	oCell.width = 130 ;
        oCell.height = 130;
        oCell.noWrap = true ;
        oCell.align = 'center' ;
	oCell.innerHTML = sLink + '<img alt="browse the folder" src="images/Folder100.gif" width="100" height="100" border="0"><\/a>' + '<br \/>' + folderTitle +  + '<br \/>' + sLinkFolder  ;

}

oListManager.AddFileToAlbum = function( fileName, fileTitle, filePhoto, fileUrl, fileSize, sType, numCell )
{
	// Create the new row.
        if (numCell%nbCell==0)
        {
	    var oRow = this.Table.insertRow(-1) ;
        }
        else
        {
            numRow = Math.floor (numCell/nbCell);
            var oRow= this.Table[numCell];
        }

	// Build the link to view the file.
        var sLink = '<a title="link the file" href="#" onclick="OpenFile(\'' + fileUrl + '\');return false;">' ;
        // Change the link if type is image since setUrl for images support more arguments
        if (sType=='Image') {
	                        sLink = '<a title="link the image" href="#" onclick="OpenImage(\'' + fileUrl + '\',\'\',\'\',\'' + fileTitle + '\');return false;">' ;
                            }

	// Get the file icon.
        if (sType!='Image')
        {
	    var sIcon = 'images/icons/' + oIcons.GetIcon( fileName ) +'.gif' ;
        }
        else
        {
	    var sIcon = fileUrl ;
        }
        if (filePhoto=='yes') {
                               var sLinkThumb = '<a href="#" onclick="OpenImage(\'' + fileUrl + '?size=thumb\',\'\',\'\',\'' + fileTitle + '\');return false;">' ;
                               var sLinkMedium = '<a href="#" onclick="OpenImage(\'' + fileUrl + '?size=medium\',\'\',\'\',\'' + fileTitle + '\');return false;">' ;
                               var sLinkFull = '<a href="#" onclick="OpenImage(\'' + fileUrl + '?size=full\',\'\',\'\',\'' + fileTitle + '\');return false;">' ;
                               sLinksPhoto = 'Size&nbsp;:&nbsp;' + sLinkThumb + 'small<\/a>&nbsp;-&nbsp;' + sLinkMedium + 'medium<\/a>&nbsp;-&nbsp;' + sLinkFull + 'full<\/a>' ;
                              }


	// Add the file icon cell.
	var oCell = oRow.insertCell(-1) ;
	oCell.width = 130 ; 
        oCell.height = 130;
        oCell.align = 'center' ;
	oCell.innerHTML = sLink + '<img alt="" src="' + sIcon + '" width="100" height="100" border="0"><\/a>' + '<br\/>' + sLink + fileTitle + '<\/a><br\/>' + sLinksPhoto + '<br\/>' + fileSize + ' KB' ;

}



function OpenFolder( folderPath )
{
	// Load the resources list for this folder.
	window.parent.frames['frmFolders'].LoadFolders( folderPath ) ;
}

function OpenFile( fileUrl )
{
	window.top.opener.SetUrl( fileUrl ) ;
	window.top.close() ;
	window.top.opener.focus() ;
}

function OpenImage( fileUrl, fileWidth, fileHeight, fileTitle )
{
	window.top.opener.SetUrl( fileUrl, fileWidth, fileHeight, fileTitle ) ;
	window.top.close() ;
	window.top.opener.focus() ;
}

function LoadResources( resourceType, folderPath )
{
	oListManager.Clear() ;
	oConnector.ResourceType = resourceType ;
	oConnector.CurrentFolder = folderPath
	oConnector.SendCommand( 'GetFoldersAndFiles', null, GetFoldersAndFilesCallBack ) ;
}

function Refresh()
{
	LoadResources( oConnector.ResourceType, oConnector.CurrentFolder ) ;
}

function GetFoldersAndFilesCallBack( fckXml )
{

        // Get the resourceType
        var oRootNode = fckXml.SelectSingleNode( 'Connector' ) ;
      	var sRootType	= oRootNode.attributes.getNamedItem('resourceType').value ;
	// Get the current folder path.
	var oNode = fckXml.SelectSingleNode( 'Connector/CurrentFolder' ) ;
	var sCurrentFolderPath	= oNode.attributes.getNamedItem('path').value ;
	var sCurrentFolderUrl	= oNode.attributes.getNamedItem('url').value ;

	// Add the Folders.	
	var oNodes = fckXml.SelectNodes( 'Connector/Folders/Folder' ) ;
	for ( var i = 0 ; i < oNodes.length ; i++ )
	{
		var sFolderName = oNodes[i].attributes.getNamedItem('name').value ;
		var sFolderTitle = oNodes[i].attributes.getNamedItem('title').value ;
                var sType =  oNodes[i].attributes.getNamedItem('type').value ;
                var sLinkbyuid =  oNodes[i].attributes.getNamedItem('linkbyuid').value ;
                var sUid =  oNodes[i].attributes.getNamedItem('uid').value ;
                if (sRootType!= 'Image')
                {
		       oListManager.AddFolder( sFolderName, sFolderTitle, sCurrentFolderPath + sFolderName + "/", sType, sLinkbyuid, sUid ) ;
                }
                else
                {
                       oListManager.AddFolderToAlbum( sFolderName, sFolderTitle, sCurrentFolderPath + sFolderName + "/", sType, sLinkbyuid, sUid, i ) ;
                       // need j to continue in the same row or table
                       var j= i;
                }
	}
	// Add the Files.	
	var oNodes = fckXml.SelectNodes( 'Connector/Files/File' ) ;
	for ( var i = 0 ; i < oNodes.length ; i++ )
	{
		var sFileName = oNodes[i].attributes.getNamedItem('name').value ;
		var sFileSize = oNodes[i].attributes.getNamedItem('size').value ;
		var sFileTitle = oNodes[i].attributes.getNamedItem('title').value ;
		var sFilePhoto = oNodes[i].attributes.getNamedItem('photo').value ;
                var sLinkbyuid =  oNodes[i].attributes.getNamedItem('linkbyuid').value ;
                var sUid =  oNodes[i].attributes.getNamedItem('uid').value ;
                var sType =  oNodes[i].attributes.getNamedItem('type').value ;
                var sIsAttach =  oNodes[i].attributes.getNamedItem('isattach').value ;
                var sAttachId =  oNodes[i].attributes.getNamedItem('attachid').value ;
                var sFileUrl = sCurrentFolderUrl + sFileName ;
                if (sLinkbyuid=='yes' && sUid !='') {
                                                     sFileUrl = './resolveUid/' + sUid ;
                                                     }
                if (sIsAttach=='yes' && sAttachId !='') {
                                                        sFileUrl = sFileUrl +'/' + sAttachId ;
                                                        }
                if (sAttachId !='') {
                                                        sFileName = sAttachId ;
                                                        }

                if (sRootType!= 'Image')
                {
		       oListManager.AddFile( sFileName, sFileTitle, sFilePhoto, sFileUrl, sFileSize, sType ) ;
                else
                {
                       oListManager.AddFileToAlbum( sFileName, sFileTitle, sFilePhoto, sFileUrl, sFileSize, sType, j+i ) ;
                }	
        }
}

window.onload = function()
{
	oListManager.Init() ;
	window.top.IsLoadedResourcesList = true ;
}