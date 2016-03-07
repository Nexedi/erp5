/*
Copyright (c) 2011-2012 Nexedi SARL and Contributors. All Rights Reserved.

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

function setCreationMode (sel) {
  // default is cloning
  var action      = 'clone';
  var action_name = 'Clone &amp; Edit';
  var icon        = 'admin_toolbox_clone_document.png';
  var name        = 'Base_cloneContent:method';
  var clone_display = 'inline';
  var new_title   = '';

  // a portal type is given, so create a new document
  var portal_type = sel.options[sel.selectedIndex].value;
  if (portal_type != 'None') {
    action      = 'new';
    action_name = 'Create New &amp; Edit';
    icon        = 'admin_toolbox_new_document.png';
    name        = 'Base_newContent:method';
    clone_display = 'none';
    new_title   = 'Create New Document';
  }

  // update action dependent values
  document.getElementById('create_new_document_title').innerHTML = new_title;
  document.getElementById('clone_document_title'     ).style.display = clone_display;
  document.getElementById('duplicate_document_action').innerHTML = action_name;

  // replace the action icon
  document.getElementById('clone_action_icon').src = eval(action + '_icon.src');

  // update action button title
  var button   = document.getElementById('clone_action_button');
  button.title = action_name;
  button.name  = name;
}

function initialize_toolbar(){
  /* initialize all toolbar menu items */

  if (document.images) {
    clone_icon = new Image();
    new_icon   = new Image();
    clone_icon.src = 'admin_toolbox_clone_document.png';
    new_icon.src   = 'admin_toolbox_new_document.png';
  }
          
  $("li.toolboxSection").each(
    function (index, menu){
      menu = $(this);
      var menu_title = menu.children("h3.menu_title").first();
      var item = menu.children("div.menu").first();
      menu_title.bind("click", function (){display_menu(item);} );
  });}

function display_menu(clicked_item){
  /* when called funtion will display current menu and hide rest */
  clicked_item.toggle();
  $("li.toolboxSection").each(
    function (index, menu){
      menu = $(this);
      var item = menu.children("div.menu").first();
      if (item.parent().attr("id") != clicked_item.parent().attr("id")) {item.hide();}
  });}

$(document).ready(initialize_toolbar);
