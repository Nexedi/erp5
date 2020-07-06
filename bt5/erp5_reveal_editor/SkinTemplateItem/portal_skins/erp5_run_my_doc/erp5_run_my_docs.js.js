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

//Add indentation to an HTML element
function addIndentation(container, first, level){
  var children = container.children;
  var text;
  var n = children.length;
  if(first){
    text = container.innerHTML.trim().replace('>', '>\n').split('\n');
    var m = text.length;
    for(var i = 0; i < m; i++){
      text[i] = text[i].trim();
    }
  }
  else
    text = container.innerHTML.trim().split('\n');
  if(n == 0 && text.length == 1)
    container.innerHTML = text[0];
  else if(n == 0) {
    container.innerHTML = '\n  ' + text.join('\n  ') + '\n';
  }
  else {
    container.innerHTML = text.join('\n');
    text = '';
    children = container.childNodes;
    n = children.length;
    for(var i = 0; i < n; i++){
      var child = children[i];
      var addNewLine = false;
      if(child.nodeType == 1){
        text += addIndentation(child, false, 0);
        addNewLine = child.tagName.length > 1 && child.tagName != 'P' && i < n - 1;
      }
      else{
        var textNotEmpty = child.textContent.trim() != '';
        if(textNotEmpty)
          text += child.textContent;
        addNewLine = textNotEmpty && child.textContent.search('\n') > -1 && i < n - 1;
      }
      if(addNewLine)
        text += '\n';
    }
    if(first){
      text = container.innerHTML.split('\n');
      var result = '\n  ';
      first = true;
      n = text.length;
      for(var i = 0; i < n; i++){
        if(text[i].trim() != ''){
          if(first){
            first = false;
            result += text[i];
          }
          else
            result += '\n  ' + text[i];
        }
      }
      result += '\n';
      container.innerHTML = result;
    }
    else
      container.innerHTML = '\n  ' + text.split('\n').join('\n  ') + '\n';
  }
  var element = document.createElement('div');
  element.appendChild(container.cloneNode(true));
  var whitespaces = Array(level + 1).join('  ');
  return whitespaces + element.innerHTML.split('\n').join('\n' + whitespaces);
}

function indent(container, level){
  return addIndentation(container, true, level);
}