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

var slideList, textContent, testPageHTML, addSlideIframe, addSlideIframeContents, editSlideIframe, editSlideIframeContents, slideNumber;
var $dialogEdit;

function isUrl(s) {
  // Test if the string is a URL or a relative path (contains a/b/..)
  var regexurl = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/
  return regexurl.test(s) || (s.split("?")[0].indexOf("/") != -1);
}

//Remove a slide
function removeClick(trigger){
  slideNumber = parseInt($(trigger).attr('id').split('_')[2]);
  $("#list > section:eq("+slideNumber+")").remove();
  $(".remove_slide_button").filter(':last').remove();
  $(".edit_slide_button").filter(':last').remove();
  updateTextContent();
  return false;
}

//Edit a slide
function editClick(trigger){
  slideNumber = parseInt($(trigger).attr('id').split('_')[2]);
  $dialogEdit.dialog('open');
  return false;
}

//Display edit and remove buttons when hovered
function slideHover(trigger){
  slideNumber = $('#list > section').index($(trigger));
  $('#edit_slide_' + slideNumber).css({'opacity': '.50', 'filter' : 'alpha(opacity=50)'});
  $('#remove_slide_' + slideNumber).css({'opacity': '.50', 'filter' : 'alpha(opacity=50)'});
}

//Hide edit and remove buttons when the mouse gets out of the slide
function slideOut(trigger){
  slideNumber = $('#list > section').index($(trigger));
  $('#edit_slide_' + slideNumber).css({'opacity': '0', 'filter' : 'alpha(opacity=0)'});
  $('#remove_slide_' + slideNumber).css({'opacity': '0', 'filter' : 'alpha(opacity=0)'});
}

//Set opacity to maximum when a button is hovered (not possible through pure css, since the buttons are not children of the corresponding slides)
function buttonHover(trigger){
  $(trigger).css({'opacity': '1', 'filter' : 'alpha(opacity=100)'});
}


//Set opacity to half once the mouse gets out
function buttonOut(trigger){
  $(trigger).css({'opacity': '0.5', 'filter' : 'alpha(opacity=50)'});
}

//Create an empty test
function createTest(){
  var table = $('<table>');
  var test = $('<test>').append(table);
  table.attr('class', "test");
  table.attr('cellpadding', "1");
  table.attr('cellspacing', "1");
  table.attr('border', "1");
  table.attr('style', "display:none;");
  table.append($('<tbody>'));
  return test;
}

//Add template test line to a test
function appendTestLine(test, method, arg0, arg1){
  var tr = $('<tr>');
  tr.append($('<td>').text(method));
  tr.append($('<td>').text(arg0));
  tr.append($('<td>').text(arg1));
  $('tbody', test).append(tr);
}

//Update HTML content of the test page
function updateTextContent(){
  body.empty();
  var images = $('#list > section > img');
  removeImagesURLAttrib(images,'display');
  removeImagesURLAttrib(images,'timestamp');
  // changeImagesURLAttrib(images,'format','');
  body.append($('#list > section').clone());
  // changeImagesURLAttrib(images,'display','xsmall');
  body[0].innerHTML = indent(body[0].cloneNode(true), 2);
  $(textContent).text(body[0].innerHTML);
}

function updateImageInput(frameContent){          
  var className = $('select[name="field_your_slide_type"]', frameContent).val();
  if (className == 'Screenshot' || className == 'Illustration') {
    $('input[name="field_your_image_caption"]', frameContent).parent().parent().removeClass('hidden');
    if (!$('input[name="field_your_upload_image"]', frameContent).is(':checked')) {
     $('input[name="field_your_image_url"]', frameContent).parent().parent().removeClass('hidden');
     }
    $('input[name="field_your_upload_image"]', frameContent).parent().parent().removeClass('hidden');
  }
  else {
    $('input[name="field_your_image_caption"]', frameContent).parent().parent().addClass('hidden');
    $('input[name="field_your_image_url"]', frameContent).parent().parent().addClass('hidden');
    $('input[name="field_your_image_id"]', frameContent).parent().parent().addClass('hidden');
    $('input[name="field_your_file"]', frameContent).parent().parent().addClass('hidden');
    $('input[name="field_your_upload_image"]', frameContent).parent().parent().addClass('hidden');
    $('input[name="field_your_upload_image"]', frameContent).attr('checked', false);
  }
}

function updateUploadImageInput(frameContent){
  var className = $('select[name="field_your_slide_type"]', frameContent).val();
  if ($('input[name="field_your_upload_image"]', frameContent).is(':checked')) {
    $('input[name="field_your_file"]', frameContent).parent().parent().removeClass('hidden');
    $('input[name="field_your_image_url"]', frameContent).parent().parent().addClass('hidden');;
    $('input[name="field_your_image_id"]', frameContent).parent().parent().removeClass('hidden')
    $('input[name="field_your_image_id"]', frameContent).removeClass('hidden');
    var targetFrameContent = frameContent;
    image_id = $('input[name="field_your_image_id"]', frameContent).val()
    if (isUrl(image_id) || image_id == "") {
      get_image_id_url = 'TestPage_getNextImageID?title=' + $('input[name="field_your_chapter_title"]', frameContent).val() + '&slide_type=' + className
      $.get(get_image_id_url, function(data, textStatus, jqXHR){
        $('input[name="field_your_image_id"]', targetFrameContent).val(data);
        });
    }
  } else {
    $('input[name="field_your_file"]', frameContent).parent().parent().addClass('hidden');
    $('input[name="field_your_image_id"]', frameContent).parent().parent().addClass('hidden');
    if (className == 'Screenshot' || className == 'Illustration') {
      $('input[name="field_your_image_url"]', frameContent).parent().parent().removeClass('hidden');
    }
    $('input[name="field_your_image_id"]', frameContent).val($('input[name="field_your_image_url"]', frameContent).val());
  }
}

function createNewImageTag(working_frame){
  var image = $('<img>');
  if (!$('input[name="field_your_upload_image"]', working_frame).is(':checked')) {
    image.attr('src', $('input[name="field_your_image_url"]', working_frame).val());
  } else {
    image.attr('src', $('input[name="field_your_image_id"]', working_frame).val() + '?format=');
  }
  // Bad hardcoding for type
  image.attr('type', 'image/svg+xml');
  image_caption = $('input[name="field_your_image_caption"]', working_frame).val()
  image.attr('title', image_caption).attr('alt', image_caption);
  return image
}

//Change/add a GET attribute in the src url of an image (located after the question mark in the url)
function changeImagesURLAttrib(images, attname, attval){
  var n = images.length;
  for(var i = 0; i < n; i++){
    var img = $(images[i]);
    var attrbs = img.attr('src').split('?');
    var url = attrbs[0];
    if(attrbs.length > 1 && attrbs[1].length > 0){
      attrbs = attrbs[1].split('&');
      var notFound = true;
      var j = 0;
      var p = attrbs.length;
      while(notFound && j < p){
        if(attrbs[j].split('=')[0] == attname){
          attrbs[j] = attname + '=' + attval;
          notFound = false;
        }
        j++;
      }
      if(notFound)
        img.attr('src', img.attr('src') + '&' + attname + '=' + attval);
      else
        img.attr('src', url + '?' + attrbs.join('&'));
    }
    else
      img.attr('src', url + '?' + attname + '=' + attval);
  }
}

// Remove a GET attribute in the src url of an image (located after the question mark in the url)
function removeImagesURLAttrib(images, attname){
  var n = images.length;
  for(var i = 0; i < n; i++){
    var img = $(images[i]);
    var attrbs = img.attr('src').split('?');
    var url = attrbs[0];
    if(attrbs.length > 1 && attrbs[1].length > 0){
      attrbs = attrbs[1].split('&');
      var notFound = true;
      var j = 0;
      var p = attrbs.length;
      while(notFound && j < p){
        if(attrbs[j].split('=')[0] == attname){
          attrbs.splice(j,1);
          notFound = false;
        }
        j++;
      }
      if(notFound)
        img.attr('src', img.attr('src'));
      else {
        complement = "";
        if (attrbs.length > 0)
          complement = '?' + attrbs.join('&');
        img.attr('src', url + complement);
      }
    }
    else
      img.attr('src', url);
  }
}

//Add edit and remove buttons to a slide
function appendSlideButtons(element, index){
  var button = $('<div>').attr('style','position:absolute; left:' + (element.offsetLeft + 3) + 'px; top:' + (element.offsetTop + 3) + 'px;').attr('id', 'edit_slide_' + index).addClass('edit_slide_button').hover(function(){buttonHover(this);},function(){buttonOut(this);});
  $(element).after(button);
  button = $('<div>').attr('style','position:absolute; left:' + (element.offsetLeft + element.offsetWidth - 17) + 'px; top:' + (element.offsetTop + 3) + 'px;').attr('id', 'remove_slide_' + index).addClass('remove_slide_button').hover(function(){buttonHover(this);},function(){buttonOut(this);});
  $(element).after(button);
}

$(document).ready(function(){
  $(function() {
    //Extract the slides
    textContent = document.getElementsByName('field_my_text_content')[0];
    var tmp = document.createElement('tmp');
    testPageHTML = document.createElement('html');
    testPageHTML.appendChild(document.createElement('body'));
    $(tmp).html($(textContent).text());
    $('body',testPageHTML).append($('section', tmp));
    body = $('section', testPageHTML);
    // changeImagesURLAttrib($('> img', body),'display','xsmall');
    slideList = $('#list');
    slideList.append(body);
    body = $('body', testPageHTML);   

    //Add buttons to each slides
    var sectionList = $('#list').children();
    n = sectionList.length;
    for(var i = 0; i < n; i++){
      var child = sectionList[i];
      appendSlideButtons(child, i);
    }

    //Make the slide list sortable
    $("#list").sortable({ opacity: 0.7, cursor: 'move', items: "section", update: function() {
        $('section').removeAttr('style');
        updateTextContent();
      }
    });
    
    //Configure the dialog to add a slide
    addSlideIframe = $("<iframe>");
    addSlideIframe.attr('id','iframe_add_slide');
    addSlideIframe.attr('src','TestPage_viewSlideCreator');

    addSlideIframe.load(function() {
      function initFrame(){ 
        addSlideIframeContents = addSlideIframe.contents();
        updateImageInput(addSlideIframeContents);
        updateUploadImageInput(addSlideIframeContents);
        $('input[name="field_your_upload_image"]', addSlideIframeContents).click(function() {updateUploadImageInput(addSlideIframeContents);});
        $('select[name="field_your_slide_type"]', addSlideIframeContents).change(function() {updateImageInput(addSlideIframeContents);});
        var submit_button = $("#dialog_submit_button", addSlideIframeContents).click(function(){
          var section = document.createElement("section");
          var className = $('select[name="field_your_slide_type"]', addSlideIframeContents).val();
          $(section).addClass(className.toLowerCase());
          var title = document.createElement("h1");
          $(title).html($('input[name="field_your_chapter_title"]', addSlideIframeContents).val());
          var details = document.createElement("details");
          $(details).attr("open", "true")
          $(details).html($('textarea[name="field_your_text_content"]', addSlideIframeContents).val());
          $(section).append($(title));
          var image_id = "";
          var isScreenshot = className == 'Screenshot';
          
          // Append a new slide, update HTML Code
          function appendSection(){
            $(section).append($('textarea[name="field_your_slide_content"]', addSlideIframeContents).val());
            $(section).append($(details));
            var isTested = $('input[name="field_your_tested"]', addSlideIframeContents).attr('checked');
            if((isTested == 'checked' || isTested) && (image_id != "")){
              var test = createTest();
              appendTestLine(test, "selectAndWait", "name=select_module", "label=Test Pages");
              appendTestLine(test, "verifyTextPresent", "Test Pages", "");            
              if(isScreenshot){
                appendTestLine(test, "captureEntirePageScreenshot", image_id, "");
              }
              $(section).append(test);
            } 
            slideList.append($(section));
            var i = 0;
            if ($('#list > .edit_slide_button').length > 0) {
              var i = parseInt($('#list > .edit_slide_button').filter(':last').attr('id').split('_')[2]) + 1;
            }
            appendSlideButtons(section, i);
            $('#remove_slide_' + i).click(function() {removeClick(this);});
            $('#edit_slide_' + i).click(function() {editClick(this);});
            $(section).hover(function() {slideHover(this);}, function(){slideOut(this);}).mousedown(function() {slideOut(this);});
            updateTextContent();
          }
          if(isScreenshot || className == 'Illustration') {
            image = createNewImageTag(addSlideIframeContents);
            image_id = "";
            if (!isUrl(image.attr('src'))) {
              image_id = image.attr('src');
            }
            $(section).append(image);
          }
          appendSection();
        });
      }
      setTimeout(initFrame, 0);
    });

    var $dialog = $("#dialog_add_slide")
      .dialog({
        title: "Add new slide",
        autoOpen: false,
        draggable: false,
        resizable: true,
        modal: true,
        autoResize: true,
        show: "clip",
        hide: "clip",
        width: "50%",
        height: "auto",
        position: 'center'
      });

    $dialog.append(addSlideIframe);
    $('#add_slide_button').click(function() {
      $dialog.dialog('open');
      return false;
    });

    //Configure the dialog to edit a slide
    editSlideIframe = $("<iframe>");
    editSlideIframe.attr('id','iframe_edit_slide');
    editSlideIframe.attr('src','TestPage_viewSlideEditor');

    editSlideIframe.load(function() {
      function initFrame(){ 
        if (slideNumber == null) {
          // slideNumber should be defined before try to edit.
          return false;
        }
        var slide = $('section:eq('+slideNumber+')', slideList);
        // This updates the image displayed
        var img = $('> img:first', slide);
        editSlideIframeContents = editSlideIframe.contents();
        updateUploadImageInput(editSlideIframeContents);
        $('input[name="field_your_upload_image"]', editSlideIframeContents).click(function() {updateUploadImageInput(editSlideIframeContents);});
        $('select[name="field_your_slide_type"]', editSlideIframeContents).change(function() {updateImageInput(editSlideIframeContents);});
        if(img.length > 0) {
          $('input[name="field_your_image_id"]', editSlideIframeContents).val(img.attr('src').split('?')[0]);
          $('input[name="field_your_image_caption"]', editSlideIframeContents).val(img.attr('title'));
          //if(isUrl(img.attr('src')))
          removeImagesURLAttrib(img,'timestamp');
          $('input[name="field_your_image_url"]', editSlideIframeContents).val(img.attr('src'));
        } else 
          updateImageInput(editSlideIframeContents);
                
        changeImagesURLAttrib($('> img:first', slide), 'timestamp', new Date().getTime());        
        $('input[name="field_your_chapter_title"]', editSlideIframeContents).val($('h1:first', slide).html().trim());
        if (slide.attr('class') != null) {
          $('select[name="field_your_slide_type"]', editSlideIframeContents).val(slide.attr('class').replace(/^\w/, function($0) { return $0.toUpperCase(); }));
        };
        var tmpSlide = slide.clone();
        $("h1:first, img:first, details, test", tmpSlide).remove();
        $('textarea[name="field_your_slide_content"]', editSlideIframeContents).val(tmpSlide.html().trim());
        if ($('details', slide).length > 0)
          $('textarea[name="field_your_text_content"]', editSlideIframeContents).val($('details', slide).html().trim());
        
        var hasTest = $('test', slide).length > 0;
        if(hasTest){
          $('input[name="field_your_not_tested"]', editSlideIframeContents).parent().parent().attr('class','field');
          $('input[name="field_your_tested"]', editSlideIframeContents).parent().parent().attr('class','hidden');
        }
        else{
          $('input[name="field_your_not_tested"]', editSlideIframeContents).parent().parent().attr('class','hidden');
          $('input[name="field_your_tested"]', editSlideIframeContents).parent().parent().attr('class','field');
        }

        var submit_button = $("#dialog_submit_button", editSlideIframeContents).click(function(){
          var titleContainer = $('h1:first', slide);
          var newTitle = $('input[name="field_your_chapter_title"]', editSlideIframeContents).val().trim();
          titleContainer.html(newTitle);
          var className = $('select[name="field_your_slide_type"]', editSlideIframeContents).val();
          slide.attr('class', className.toLowerCase());
          if ($('details', slide).length === 0) {
            var details = document.createElement("details");
            slide.append($(details));
          }
          $('details', slide).html($('textarea[name="field_your_text_content"]', editSlideIframeContents).val().trim());
          $('details', slide).attr("open", "true")
          $("> :not(h1:first, img:first, details, test)", slide).remove();
          // Remove also the standalone text inputed by the user.
          slide.contents().filter(function(){return this.nodeType === 3;}).remove();
          // Read from Slide editor
          $(" > h1:first, img:first", slide).filter(':last').after($('textarea[name="field_your_slide_content"]', editSlideIframeContents).val().trim());
          var image_id = "";
          var isScreenshot = className == 'Screenshot';
          function appendSection(){
            var isTested = $('input[name="field_your_tested"]', editSlideIframeContents).attr('checked');
            var removeTest = $('input[name="field_your_not_tested"]', editSlideIframeContents).attr('checked');
            if(!hasTest &&  (isTested == 'checked' || isTested) && (image_id != "")){
              var test = createTest();
              appendTestLine(test, "selectAndWait", "name=select_module", "label=Test Pages");
              appendTestLine(test, "verifyTextPresent", "Test Pages", "");            
              if(isScreenshot){
                appendTestLine(test, "captureEntirePageScreenshot", image_id, "");
              }
              slide.append(test);
            } 
            else if(hasTest &&  removeTest == 'checked' || removeTest)
              $('test', slide).remove();
            updateTextContent();
          }
          if(isScreenshot || className == 'Illustration'){
            var img = $('img:first', slide);
            if(img.length > 0){
              var image_caption = $('input[name="field_your_image_caption"]', editSlideIframeContents).val()
              if (image_caption.length > 0)
                img.attr('title', image_caption).attr('alt', image_caption);
              var image_url = $('input[name="field_your_image_url"]', editSlideIframeContents).val();
              if (isUrl(image_url)) {
                image_id = "";
              }
              img.attr('src', image_url)
            } else {
              image = createNewImageTag(editSlideIframeContents);
              image_id = "";
              if (!isUrl(image.attr('src'))) {
                image_id = image.attr('src');
              }
              $("> h1:first", slide).after(image);
            }
          } 
          appendSection();
        });
      }
        
      setTimeout(initFrame, 0);
    });

    $dialogEdit = $("#dialog_edit_slide")
      .dialog({
        title: "Edit slide",
        autoOpen: false,
        draggable: false,
        resizable: true,
        modal: true,
        autoResize: true,
        show: "clip",
        hide: "clip",
        width: "50%",
        height: "auto",
        position: 'center'
      });

    $dialogEdit.append(editSlideIframe);
    $('.edit_slide_button').click(function() {
      editClick(this);
    });

    $('.remove_slide_button').click(function() {
      removeClick(this);
    });

    $('section').hover(function() {
      slideHover(this);
    }, function(){
        slideOut(this);
    });

    $('section').mousedown(function() {
      slideOut(this);
    });      
  });
});