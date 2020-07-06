/*
Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.

This program is Free Software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/
var first = true, editedObject, counter = 0;

var offset = {'left':10,'top':10};
var colors = ['#FF0000','#00FF00','#0000FF','#FFFF00','#FF00FF','#00FFFF','#FFFFFF'];


function parseCommentLine(line){
  var textList = line.substr(1);
  textList = textList.substr(0,textList.length - 1).split(/\},\{/g);
  textList[0] = textList[0].replace(/\n/g,' ');
  return textList;
}

function createCommentLine(args){
  return '{' + args.join('},{') + '}';
}

function appendColors(object){
  var n = colors.length;
  for(var i = 0; i < n; i++){
    var color = colors[i];
    var button = $('<div>').addClass('color_button').attr('id','color_button_' + i).css('background-color', color).click(function(){
      $('#review_tooltip').css('background-color', $(this).css('background-color'));
    });
    object.append(button);
  }
}
	 
function displayToolTip(commentArray, e){
  if(editedObject == null){
    var reviewToolTip = $('#review_tooltip');
    reviewToolTip.attr('class', 'activated_review_tooltip').attr('style', 'left:' + (offset.left + e.clientX) +'px; top:'+ (offset.top + e.clientY) + 'px;');
    toolTipText = $('.tooltip_text', reviewToolTip);
    if(toolTipText.length == 0){
      reviewToolTip.append($('<span>').addClass('tooltip_text').text(commentArray[0]));
      reviewToolTip.append($('<span>').addClass('tooltip_author').text(commentArray[3]));
      reviewToolTip.css('background-color', commentArray[4]);
    }
    else{
      toolTipText.text(commentArray[0]);
      $('.tooltip_author', reviewToolTip).text(commentArray[3]);
      reviewToolTip.css('background-color', commentArray[4]);
    }
  }
}
		 
function hideToolTip(){
  if(editedObject == null)
    $('#review_tooltip').attr('class', 'desactivated_review_tooltip');
}

function changeUrl(){
  $('#label_ready').attr('class','label_document_not_ready').text('Not ready. Wait until the document is ready to start commenting.');
  document.getElementById('iframe').src = document.getElementById('value_url').value;
}

function findDocument(url){
  var doc = document;
  var iframes = $('iframe');
  var n = iframes.length, i = 0;
  while(doc.URL != url && i < n){
    doc = iframes.eq(i).contents()[0];
    i++;
  }
  return doc;
}

function findId(object){
  return parseInt(object.id.split("_")[2]);
}

function getAuthor(){
  return $('#logged_in_as', document).text().replace('Logged In as :', '').trim();
}

function validateComment(object, clicked){
  var validationRequired = clicked || (editedObject != null && editedObject.id != object.id);
  if(validationRequired){
    var text = $('#review_tooltip textarea').val();
    var color = $('#review_tooltip').css('background-color');
    //Saving
    var id = findId(editedObject);
    var commentaryListObj = $("textarea[name=field_my_annotation]", document);
    var commentaryList = commentaryListObj.val().split('\n');
    var commentArray = parseCommentLine(commentaryList[id]);
    commentArray[0] = text;
    commentArray[3] = getAuthor();
    commentArray[4] = color;
    commentaryList[id] = createCommentLine(commentArray);
    commentaryListObj.val(commentaryList.join('\n'));
    $('#review_tooltip').empty();
    $(editedObject).empty().text(text).attr('class','added_comment').css('background-color',color).css('color', color).mousemove(function(e){
      displayToolTip(commentArray, e);
    });
    editedObject = null;
    hideToolTip();
  }
  return validationRequired;
}

function editComment(object, e){
  if(editedObject == null || validateComment(object, false)){
    var text = $(object).text();
    var textarea = $('<textarea>').val(text).attr('style','width:95%;height:100%');
    var validation_button = $('<div>').addClass('validate_button').click(function(){
      validateComment(editedObject, true);
    });
    var remove_button = $('<div>').addClass('remove_button').click(function(){
      removeComment();
    });
    appendColors($('#review_tooltip').empty().attr('class', 'activated_review_tooltip').attr('style', 'left:' + (offset.left + e.clientX) +'px; top:'+ (offset.top + e.clientY) + 'px;background-color: ' + $(object).css('background-color') + ';' ).append(textarea).append(validation_button).append(remove_button));
    editedObject = object;
    textarea[0].focus();
  }
}

function removeLine(name, id){
  var obj = $("textarea[name=field_" + name + "]", document);
  var text = obj.val().split('\n');
  text.splice(id,1);
  obj.val(text.join('\n'));
}

function removeComment(){
  var id = findId(editedObject);
  $(editedObject).remove();
  removeLine("my_annotation", id);
  $('#review_tooltip').empty();
  var iframes = $('iframe');
  var n = iframes.length;
  for(var i = 0; i < n; i++){
    var comments = $('.added_comment', iframes.eq(i).contents());
    var p = comments.length;
    for(var j = 0; j < p; j++){
      var comm = comments.eq(j);
      var commId = findId(comm[0]);
      if(commId > id)
        comm.attr('id','comment_bubble_' + (commId - 1));
    }
  }
  editedObject = null;
  hideToolTip();
  counter--;
}

function addComment(commentArray, notSetup, e){
  var comment = commentArray[0], locator = commentArray[1], contextUrl = commentArray[2], author = commentArray[3], color = commentArray[4];
  var context = findDocument(contextUrl);
  var object = $(locator, context);

  if(notSetup){
    var commentaryListObj = $("textarea[name=field_my_annotation]", document);
    var commentaryList = commentaryListObj.val();
    if(commentaryList.trim() != ''){
      commentaryList += '\n';
    }
    commentaryListObj.val(commentaryList + createCommentLine([comment, locator, contextUrl, author]));
  }
  var htmlObject = object[0];
  var offset = object.offset();
  var commentObject = $('<div>').attr('style','left:' + offset.left + 'px; top:' + offset.top + 'px; width:' + htmlObject.offsetWidth + 'px; height:' + htmlObject.offsetHeight + 'px; background-color:' + color + ';color:' + color + ';').addClass('added_comment').attr('id','comment_bubble_' + counter);
  counter++;
  $(context.body).append(commentObject);
  commentObject.click(function(e){
    editComment(this, e);
  });
  commentObject.mousemove(function(e){
    displayToolTip(commentArray, e);
  });
  commentObject.mouseout(function(){
    hideToolTip();
  });
  validateComment(commentObject, false);
  if(notSetup)
    editComment(commentObject[0], e);
  else{
    commentObject.text(comment);
  }
}

function findIndex(object, locator, context){
  var i = 0;
  var objectArray = $(locator, context);
  var n = objectArray.length;
  while(i < n && !objectArray.eq(i).is(object)){
    i++;
  }
  if(i == n)
    return -1;
  else
    return i;
}

function findClassLocator(className){
  return className = '[class="' + className + '"]'; //'.' + className.replace('\n', ' ').split(' ').filter(function(a){return a != ''}).join('.');
}

function findMinimumLocator(object, parentLocator, context){
  //We know that there's no id here, so we don't check for id
  parentLocator += ' ';
  var notFound = true;
  var first = true;
  var obj = object;
  var locator = '';
  while(notFound){
    var className = obj.className;
    childLocator = obj.tagName;
    if(className != undefined && className != '')
      childLocator += findClassLocator(className);
    locator = parentLocator + childLocator;
    if($(locator, context).length == 1)
      notFound = false;
    else if($(locator, context).parent().is($(parentLocator, context))){
      var locatorPart = parentLocator + '> ' + childLocator;
      //For a mysterious reason the following line doesn't work:
      //locator = locatorPart + ':eq(' + $(obj).index($(locatorPart, context)) + ')';
      locator = locatorPart + ':eq(' + findIndex(obj, locatorPart, context) + ')';
      notFound = false;
    }
    else if(first)
      first = false;
    obj = $(obj).parent()[0];
  }
  if(first)
    return locator;
  else
    return findMinimumLocator(object, locator, context);
}

function findLocator(object, context){
  var notFound = true;
  var first = true;
  var obj = object;
  var locator = '';
  while(notFound){
    var className = obj.className;
    var objId = obj.id;
    var tagName = obj.tagName;
    if(objId != undefined && objId != ''){
      locator = '#' + objId;
      notFound = false;
    }
    else if(tagName.toLowerCase() == 'body'){
      locator = 'body';
      notFound = false;
    }
    else{
      locator = tagName;
      if(className != undefined && className != '')
        locator += findClassLocator(className);
      if($(locator, context).length == 1)
        notFound = false;
      else if(first)
        first = false;
    }
    obj = $(obj).parent()[0];
  }
  if(first)
    return locator;
  else
    return findMinimumLocator(object, locator, context);
}

function findContext(object){
  var obj = object;
  while(obj.tagName.toLowerCase() != 'body'){
    obj = obj.parentNode;
  }
  return obj.parentNode.parentNode;
}

function clickObject(object, e){
  var context = findContext(object);
  var locator = findLocator(object, context);
  var contextUrl = context.URL;
  addComment(['', locator, contextUrl, getAuthor(),'#FF0000'], true, e);
  return false;
}

$(document).ready(function(){
  $('iframe').load(function() {
    var frameBody = $(this).contents()[0].body;
    $('a', frameBody).removeAttr('onclick').removeAttr('href');
    $(':not(:has(*))', frameBody).removeAttr('onclick').removeAttr('href').click(function(e) {
      clickObject(this, e);
      return false;
    });
    var cssLink = document.createElement("link");
    cssLink.href = document.URL.split('review_module')[0] + "reviewer.css"; 
    cssLink.rel = "stylesheet"; 
    cssLink.type = "text/css"; 
    this.contentDocument.body.appendChild(cssLink);
    var commentaryListObj = $("textarea[name=field_my_annotation]", document);
    var commentaryList = commentaryListObj.val().split('\n');
    var n = commentaryList.length;
    for(var i = 0; i < n; i++){
      if(i != 0 || commentaryList[i] != '')
        addComment(parseCommentLine(commentaryList[i]), false, undefined);
    }
    $('#label_ready').attr('class','label_document_ready').text('Ready. You just have to click on an HTML element to comment it. Doesnt work with simple text (yet).');
  });
});
