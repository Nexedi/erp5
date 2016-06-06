<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="DTMLDocument" module="OFS.DTMLDocument"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>reviewer.js</string> </value>
        </item>
        <item>
            <key> <string>_vars</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>globals</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>raw</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.\n
\n
This program is Free Software; you can redistribute it and/or\n
modify it under the terms of the GNU General Public License\n
as published by the Free Software Foundation; either version 2\n
of the License, or (at your option) any later version.\n
\n
This program is distributed in the hope that it will be useful,\n
but WITHOUT ANY WARRANTY; without even the implied warranty of\n
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n
GNU General Public License for more details.\n
\n
You should have received a copy of the GNU General Public License\n
along with this program; if not, write to the Free Software\n
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.\n
*/\n
var first = true, editedObject, counter = 0;\n
\n
var offset = {\'left\':10,\'top\':10};\n
var colors = [\'#FF0000\',\'#00FF00\',\'#0000FF\',\'#FFFF00\',\'#FF00FF\',\'#00FFFF\',\'#FFFFFF\'];\n
\n
\n
function parseCommentLine(line){\n
  var textList = line.substr(1);\n
  textList = textList.substr(0,textList.length - 1).split(/\\},\\{/g);\n
  textList[0] = textList[0].replace(/\\n/g,\' \');\n
  return textList;\n
}\n
\n
function createCommentLine(args){\n
  return \'{\' + args.join(\'},{\') + \'}\';\n
}\n
\n
function appendColors(object){\n
  var n = colors.length;\n
  for(var i = 0; i < n; i++){\n
    var color = colors[i];\n
    var button = $(\'<div>\').addClass(\'color_button\').attr(\'id\',\'color_button_\' + i).css(\'background-color\', color).click(function(){\n
      $(\'#review_tooltip\').css(\'background-color\', $(this).css(\'background-color\'));\n
    });\n
    object.append(button);\n
  }\n
}\n
\t \n
function displayToolTip(commentArray, e){\n
  if(editedObject == null){\n
    var reviewToolTip = $(\'#review_tooltip\');\n
    reviewToolTip.attr(\'class\', \'activated_review_tooltip\').attr(\'style\', \'left:\' + (offset.left + e.clientX) +\'px; top:\'+ (offset.top + e.clientY) + \'px;\');\n
    toolTipText = $(\'.tooltip_text\', reviewToolTip);\n
    if(toolTipText.length == 0){\n
      reviewToolTip.append($(\'<span>\').addClass(\'tooltip_text\').text(commentArray[0]));\n
      reviewToolTip.append($(\'<span>\').addClass(\'tooltip_author\').text(commentArray[3]));\n
      reviewToolTip.css(\'background-color\', commentArray[4]);\n
    }\n
    else{\n
      toolTipText.text(commentArray[0]);\n
      $(\'.tooltip_author\', reviewToolTip).text(commentArray[3]);\n
      reviewToolTip.css(\'background-color\', commentArray[4]);\n
    }\n
  }\n
}\n
\t\t \n
function hideToolTip(){\n
  if(editedObject == null)\n
    $(\'#review_tooltip\').attr(\'class\', \'desactivated_review_tooltip\');\n
}\n
\n
function changeUrl(){\n
  $(\'#label_ready\').attr(\'class\',\'label_document_not_ready\').text(\'Not ready. Wait until the document is ready to start commenting.\');\n
  document.getElementById(\'iframe\').src = document.getElementById(\'value_url\').value;\n
}\n
\n
function findDocument(url){\n
  var doc = document;\n
  var iframes = $(\'iframe\');\n
  var n = iframes.length, i = 0;\n
  while(doc.URL != url && i < n){\n
    doc = iframes.eq(i).contents()[0];\n
    i++;\n
  }\n
  return doc;\n
}\n
\n
function findId(object){\n
  return parseInt(object.id.split("_")[2]);\n
}\n
\n
function getAuthor(){\n
  return $(\'#logged_in_as\', document).text().replace(\'Logged In as :\', \'\').trim();\n
}\n
\n
function validateComment(object, clicked){\n
  var validationRequired = clicked || (editedObject != null && editedObject.id != object.id);\n
  if(validationRequired){\n
    var text = $(\'#review_tooltip textarea\').val();\n
    var color = $(\'#review_tooltip\').css(\'background-color\');\n
    //Saving\n
    var id = findId(editedObject);\n
    var commentaryListObj = $("textarea[name=field_my_annotation]", document);\n
    var commentaryList = commentaryListObj.val().split(\'\\n\');\n
    var commentArray = parseCommentLine(commentaryList[id]);\n
    commentArray[0] = text;\n
    commentArray[3] = getAuthor();\n
    commentArray[4] = color;\n
    commentaryList[id] = createCommentLine(commentArray);\n
    commentaryListObj.val(commentaryList.join(\'\\n\'));\n
    $(\'#review_tooltip\').empty();\n
    $(editedObject).empty().text(text).attr(\'class\',\'added_comment\').css(\'background-color\',color).css(\'color\', color).mousemove(function(e){\n
      displayToolTip(commentArray, e);\n
    });\n
    editedObject = null;\n
    hideToolTip();\n
  }\n
  return validationRequired;\n
}\n
\n
function editComment(object, e){\n
  if(editedObject == null || validateComment(object, false)){\n
    var text = $(object).text();\n
    var textarea = $(\'<textarea>\').val(text).attr(\'style\',\'width:95%;height:100%\');\n
    var validation_button = $(\'<div>\').addClass(\'validate_button\').click(function(){\n
      validateComment(editedObject, true);\n
    });\n
    var remove_button = $(\'<div>\').addClass(\'remove_button\').click(function(){\n
      removeComment();\n
    });\n
    appendColors($(\'#review_tooltip\').empty().attr(\'class\', \'activated_review_tooltip\').attr(\'style\', \'left:\' + (offset.left + e.clientX) +\'px; top:\'+ (offset.top + e.clientY) + \'px;background-color: \' + $(object).css(\'background-color\') + \';\' ).append(textarea).append(validation_button).append(remove_button));\n
    editedObject = object;\n
    textarea[0].focus();\n
  }\n
}\n
\n
function removeLine(name, id){\n
  var obj = $("textarea[name=field_" + name + "]", document);\n
  var text = obj.val().split(\'\\n\');\n
  text.splice(id,1);\n
  obj.val(text.join(\'\\n\'));\n
}\n
\n
function removeComment(){\n
  var id = findId(editedObject);\n
  $(editedObject).remove();\n
  removeLine("my_annotation", id);\n
  $(\'#review_tooltip\').empty();\n
  var iframes = $(\'iframe\');\n
  var n = iframes.length;\n
  for(var i = 0; i < n; i++){\n
    var comments = $(\'.added_comment\', iframes.eq(i).contents());\n
    var p = comments.length;\n
    for(var j = 0; j < p; j++){\n
      var comm = comments.eq(j);\n
      var commId = findId(comm[0]);\n
      if(commId > id)\n
        comm.attr(\'id\',\'comment_bubble_\' + (commId - 1));\n
    }\n
  }\n
  editedObject = null;\n
  hideToolTip();\n
  counter--;\n
}\n
\n
function addComment(commentArray, notSetup, e){\n
  var comment = commentArray[0], locator = commentArray[1], contextUrl = commentArray[2], author = commentArray[3], color = commentArray[4];\n
  var context = findDocument(contextUrl);\n
  var object = $(locator, context);\n
\n
  if(notSetup){\n
    var commentaryListObj = $("textarea[name=field_my_annotation]", document);\n
    var commentaryList = commentaryListObj.val();\n
    if(commentaryList.trim() != \'\'){\n
      commentaryList += \'\\n\';\n
    }\n
    commentaryListObj.val(commentaryList + createCommentLine([comment, locator, contextUrl, author]));\n
  }\n
  var htmlObject = object[0];\n
  var offset = object.offset();\n
  var commentObject = $(\'<div>\').attr(\'style\',\'left:\' + offset.left + \'px; top:\' + offset.top + \'px; width:\' + htmlObject.offsetWidth + \'px; height:\' + htmlObject.offsetHeight + \'px; background-color:\' + color + \';color:\' + color + \';\').addClass(\'added_comment\').attr(\'id\',\'comment_bubble_\' + counter);\n
  counter++;\n
  $(context.body).append(commentObject);\n
  commentObject.click(function(e){\n
    editComment(this, e);\n
  });\n
  commentObject.mousemove(function(e){\n
    displayToolTip(commentArray, e);\n
  });\n
  commentObject.mouseout(function(){\n
    hideToolTip();\n
  });\n
  validateComment(commentObject, false);\n
  if(notSetup)\n
    editComment(commentObject[0], e);\n
  else{\n
    commentObject.text(comment);\n
  }\n
}\n
\n
function findIndex(object, locator, context){\n
  var i = 0;\n
  var objectArray = $(locator, context);\n
  var n = objectArray.length;\n
  while(i < n && !objectArray.eq(i).is(object)){\n
    i++;\n
  }\n
  if(i == n)\n
    return -1;\n
  else\n
    return i;\n
}\n
\n
function findClassLocator(className){\n
  return className = \'[class="\' + className + \'"]\'; //\'.\' + className.replace(\'\\n\', \' \').split(\' \').filter(function(a){return a != \'\'}).join(\'.\');\n
}\n
\n
function findMinimumLocator(object, parentLocator, context){\n
  //We know that there\'s no id here, so we don\'t check for id\n
  parentLocator += \' \';\n
  var notFound = true;\n
  var first = true;\n
  var obj = object;\n
  var locator = \'\';\n
  while(notFound){\n
    var className = obj.className;\n
    childLocator = obj.tagName;\n
    if(className != undefined && className != \'\')\n
      childLocator += findClassLocator(className);\n
    locator = parentLocator + childLocator;\n
    if($(locator, context).length == 1)\n
      notFound = false;\n
    else if($(locator, context).parent().is($(parentLocator, context))){\n
      var locatorPart = parentLocator + \'> \' + childLocator;\n
      //For a mysterious reason the following line doesn\'t work:\n
      //locator = locatorPart + \':eq(\' + $(obj).index($(locatorPart, context)) + \')\';\n
      locator = locatorPart + \':eq(\' + findIndex(obj, locatorPart, context) + \')\';\n
      notFound = false;\n
    }\n
    else if(first)\n
      first = false;\n
    obj = $(obj).parent()[0];\n
  }\n
  if(first)\n
    return locator;\n
  else\n
    return findMinimumLocator(object, locator, context);\n
}\n
\n
function findLocator(object, context){\n
  var notFound = true;\n
  var first = true;\n
  var obj = object;\n
  var locator = \'\';\n
  while(notFound){\n
    var className = obj.className;\n
    var objId = obj.id;\n
    var tagName = obj.tagName;\n
    if(objId != undefined && objId != \'\'){\n
      locator = \'#\' + objId;\n
      notFound = false;\n
    }\n
    else if(tagName.toLowerCase() == \'body\'){\n
      locator = \'body\';\n
      notFound = false;\n
    }\n
    else{\n
      locator = tagName;\n
      if(className != undefined && className != \'\')\n
        locator += findClassLocator(className);\n
      if($(locator, context).length == 1)\n
        notFound = false;\n
      else if(first)\n
        first = false;\n
    }\n
    obj = $(obj).parent()[0];\n
  }\n
  if(first)\n
    return locator;\n
  else\n
    return findMinimumLocator(object, locator, context);\n
}\n
\n
function findContext(object){\n
  var obj = object;\n
  while(obj.tagName.toLowerCase() != \'body\'){\n
    obj = obj.parentNode;\n
  }\n
  return obj.parentNode.parentNode;\n
}\n
\n
function clickObject(object, e){\n
  var context = findContext(object);\n
  var locator = findLocator(object, context);\n
  var contextUrl = context.URL;\n
  addComment([\'\', locator, contextUrl, getAuthor(),\'#FF0000\'], true, e);\n
  return false;\n
}\n
\n
$(document).ready(function(){\n
  $(\'iframe\').load(function() {\n
    var frameBody = $(this).contents()[0].body;\n
    $(\'a\', frameBody).removeAttr(\'onclick\').removeAttr(\'href\');\n
    $(\':not(:has(*))\', frameBody).removeAttr(\'onclick\').removeAttr(\'href\').click(function(e) {\n
      clickObject(this, e);\n
      return false;\n
    });\n
    var cssLink = document.createElement("link");\n
    cssLink.href = document.URL.split(\'review_module\')[0] + "reviewer.css"; \n
    cssLink.rel = "stylesheet"; \n
    cssLink.type = "text/css"; \n
    this.contentDocument.body.appendChild(cssLink);\n
    var commentaryListObj = $("textarea[name=field_my_annotation]", document);\n
    var commentaryList = commentaryListObj.val().split(\'\\n\');\n
    var n = commentaryList.length;\n
    for(var i = 0; i < n; i++){\n
      if(i != 0 || commentaryList[i] != \'\')\n
        addComment(parseCommentLine(commentaryList[i]), false, undefined);\n
    }\n
    $(\'#label_ready\').attr(\'class\',\'label_document_ready\').text(\'Ready. You just have to click on an HTML element to comment it. Doesnt work with simple text (yet).\');\n
  });\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
