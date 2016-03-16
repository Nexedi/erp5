/*
Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
                   Sebastien Robin <seb@nexedi.com>

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

/*
Note: this JavaScript is used to make parallel list field more user friendly
*/

$(function() {

  // Make the parallel list field adding more elements automatically.
  $('.input .extensible_parallel_list_field').change(function(event) {
    event.preventDefault();
    var select_element = $(event.target)
    var add_element = true;
    var to_clone_element = select_element
    var parent = select_element.parent()
    if (parent[0].nodeName == 'DIV') {
      to_clone_element = parent
      parent = parent.parent()
    }
    var select_list = parent.find('select')
    for(var x = select_list.length; x;) {
      current_select = select_list[--x]
      if (current_select.selectedIndex == 0)
      {
        add_element = false;
      }
    }
    if (add_element) {
      parent.append(jQuery('<label>&nbsp;</label>'))
      var cloned_element = to_clone_element.clone(true)
      cloned_element[0].selectedIndex = 0
      cloned_element.appendTo(parent)
      parent.append(jQuery('<p class="clear">'))
    }
  });

});
