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

var slideList, textContent, testPageHTML, editedElement;

//Copy the content of text to textareas (switch this row to edit mode)
function editContent(container){
  if(editedElement != undefined)
    validateContent();
  editedElement = container;
  var children = container.children();
  // add a new validation button
  children.eq(1).empty().append($('<div>').addClass('validate').click(function() {validationClick(this);}));
  var n = children.length;
  for(var i = 2; i < n; i++)
    switchToEditMode(children.eq(i));
}

//Copy the content of textareas to text (switch this row to standard mode), and update the html code with this test line
function validateContent(){
  var children = editedElement.children();
  // add a new edit button
  children.eq(1).empty().append($('<div>').addClass('edit').click(function() {editClick(this);}));
  var n = children.length;
  for(var i = 2; i < n; i++)
    switchToValidated(children.eq(i));
  editedElement = undefined;
  updateTextContent();
}

//Copy the content of an input contained in container, and paste it as text of the container (transform a textarea into a text)
function switchToValidated(container){
  var text = container.children().val();
  container.empty().text(text);
}

//Copy the text contained in container, and paste it in a textarea (transform a text into a textarea)
function switchToEditMode(container){
  var textarea = $('<textarea>').val(container.text()).attr('style','width:95%;height:16px');
  container.empty().append(textarea);
}

//Remove a row
function removeClick(trigger){
  $(trigger).parent().parent().remove();
  updateTextContent();
  return false;
}

//Edit a row
function editClick(trigger){
  editContent($(trigger).parent().parent());
  return false;
}

//Validate a row
function validationClick(trigger){
  validateContent();
  return false;
}

//Update the HTML code of the test page
function updateTextContent(){
  var testLines = $('#list > tr'), testBody;
  var i = 0, n = testLines.length, sectionIndex = -1;
  for(i = 0; i < n; i++){
    var line = testLines.eq(i);
    var firstCol = line.children().filter(':first');
    var tagName = firstCol[0].tagName;
    if(tagName == 'TH' && (firstCol.attr('class') == '' || firstCol.attr('class') == undefined)){
      sectionIndex++;
      var currentSection = $('section:eq(' + sectionIndex + ')', testPageHTML);
      testBody = $('test tbody', currentSection);
      if(testBody == undefined || testBody.length == 0){
        currentSection.append($('<test>').append($('<table>').attr("style","display: none;").addClass("test").append($('<tbody>'))));
        testBody = $('test tbody', currentSection);
      }
      else
        testBody.empty();
    }
    else if(tagName == 'TD'){
      var lineToAdd = line.clone();
      $('td:eq(0), td:eq(1)', lineToAdd).remove();
      testBody.append(lineToAdd);
    }
  }
  $(textContent).text($(indent($(testPageHTML)[0], 2))[0].innerHTML);
}

//Add an edit button and a remove button to a line
function prependEditButtons(element){
  return element.prepend($('<td>').append($('<div>').addClass('edit'))).prepend($('<td>').append($('<div>').addClass('remove')));
}

$(document).ready(function(){
  $(function() {
    // Extract slide list
    textContent = document.getElementsByName('field_my_text_content')[0];
    var tmp = document.createElement('tmp');
    $(tmp).html($(textContent).text());

    testPageHTML = document.createElement('content');
    $(testPageHTML).append($('section', tmp));

    $('#test_table > thead').append($('test thead > tr > th', testPageHTML).attr('colspan',5).parent());
    slideList = $('section', testPageHTML);

    var n = slideList.length;
    var body = $('#test_table > tbody');

    // Prepare chapters, and buttons to add instruction for each chapter
    for(var i = 0; i < n; i++){
      var slide = slideList.eq(i);
      body.append($('<tr>').append($('<th>').attr('colspan',5).html($('h1:first',slide).html())));
      body.append($('test tbody > tr',slide));
      body.append($('<tr>').append($('<th>').addClass('add_instr_button').attr('id','add_instr_' + i).attr('colspan',5).text('Add test instruction')));
      body.append($('<tr>').append($('<th>').addClass('add_metal_button').attr('id','add_metal_' + i).attr('colspan',5).text('Add metal instruction')));
    }
    prependEditButtons($('#test_table tr:has(td)'));

    $("#list").sortable({ opacity: 0.7, cursor: 'move', items: "tr:has(td)", update: function() {
        updateTextContent();
      }
    });
     $('#list .remove').click(function() {
      removeClick(this);
    });

    $('#list .edit').click(function() {
      editClick(this);
    });

    $('#list .validate').click(function() {
      validationClick(this);
    });

    $('#list .add_instr_button').click(function() {
      var newElement = prependEditButtons($('<tr>').append('<td><td><td>'));
      $('.remove', newElement).click(function(){removeClick(this);});
      $(this).parent().before(newElement);
      editContent(newElement);
    });

    $('#list .add_metal_button').click(function() {
      var i = parseInt($(this).attr('id').split('_')[2]);
      var brother = $('#add_instr_' + i, $(this).parent().parent()).parent();
      var newElement = prependEditButtons($('<tr>').append($('<td>').attr('colspan',3)));
      $('.remove', newElement).click(function(){removeClick(this);});
      brother.before(newElement);
      editContent(newElement);
    });
  });
});