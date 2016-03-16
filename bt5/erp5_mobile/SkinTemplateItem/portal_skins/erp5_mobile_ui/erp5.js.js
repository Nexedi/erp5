/*
Copyright (c) 20xx-2006 Nexedi SARL and Contributors. All Rights Reserved.

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
function submitAction(form,act) {
  form.action = act;
  form.submit();
}

function isListMode() {
  if (document.getElementById("listmodeflag"))
    {
      alert("ca list");
      return(1);
    }
  else
    {
      alert("ca lsit pas");
      return(0);
    }
}

function affOptions () {
var sc = document.getElementById("options_list");
if (!sc)
  {
    return(0);
  }
if (sc.style.display == "none")
  {
    sc.style.display = "block";
  }
else
  {
    sc.style.display = "none";
  }
}


function affShortcuts () {
var sc = document.getElementById("shortcuts");
if (!sc)
  {
    return(0);
  }
if (sc.style.display == "none")
  {
    sc.style.display = "block";
  }
else
  {
    sc.style.display = "none";
  }
}

function simple_aff(dynamic_check_field) {

 if(dynamic_check_field) 
 {
  form_id=dynamic_check_field.split("listbox_")
  max_lenght_field_id=form_id[0]+"listbox_listMax"
  max_item_field_id=form_id[0]+"listbox_itemMax";
  span_field_id=form_id[0]+"listbox_check";
  var max_lenght = document.getElementById(max_lenght_field_id).value;
  var max_item = document.getElementById(max_item_field_id).value;
  var span_field = document.getElementById(span_field_id);

  if (span_field.className=="div_short_mode") {
     var span_className="div_short_mode"
  }
  else {
     var span_className="div_normal_mode"
  }

  for (b = 0; b < max_item; b++)
  {
   for (a = 0; a < max_lenght; a++)
    { var foo =form_id[0]+ 'listbox_' + b + 'data' + a;
      var target = document.getElementById(foo);
      if (span_className=="div_short_mode")
       {
        target.style.display = "inline";
        span_field.className="div_normal_mode"
       }
      else
       {
        target.style.display = "none";
        span_field.className="div_short_mode"
       }
    }
  }
 }
}

function applyHiddenType() {

 if(document.getElementById("listbox_listMax"))
 { var max_item = document.getElementById("listbox_itemMax").value;
   var max_lenght = document.getElementById("listbox_listMax").value;
   hideListItems('',max_item, max_lenght)
 }

/* XXX Hard code, get the number of box with show/hide mode */
 for (i = 0; i < 5; i++) {
  form_id = "x"+i+"_"
  var max_lenght_field_id=form_id+"listbox_listMax"
  var max_item_field_id=form_id+"listbox_itemMax"
  if(document.getElementById(max_lenght_field_id) && document.getElementById(max_item_field_id) )
   { 
    var max_item = document.getElementById(max_item_field_id).value;
    var max_lenght = document.getElementById(max_lenght_field_id).value;
    hideListItems(form_id,max_item, max_lenght)
   }
  }
  affShortcuts ();
  showSearchSelectedColumn();
}

function hideListItems(form_id, max_item, max_length)
{
 check=form_id+"listbox_check";
 for (b = 0; b < max_item; b++)
 {
  for (a = 0; a < max_length; a++)
   { var foo =form_id+ 'listbox_' + b + 'data' + a;
     var target = document.getElementById(foo);
     if(target) 
       target.style.display = "none";
   }
  }
}

function showSearchSelectedColumn()
{
  var select_search_field      = document.getElementById("select_search_field");
//   var search_value_list_count  = select_search_field.length;
  var search_value_list_count  = document.getElementById("search_value_list_count").value;
  var selected_field           = select_search_field.options[select_search_field.selectedIndex];
  var selected_field_value     = select_search_field.options[select_search_field.selectedIndex].value;
  var selected_field_id        = document.getElementById('input'+selected_field.index).id;

 if(selected_field) {
  for (a = 0; a < search_value_list_count; a++)
   { var foo ='input' + a;
     var target_name = document.getElementById(foo);
     if(target_name) {
       var target_id   = target_name.id;
       target_name.style.display=(target_id==selected_field_id)?'inline':'none';
       if(target_id==selected_field_id)
         select_search_field.selectedIndex=a;
     }
   }
  }
  else {
    for (a = 0; a < search_value_list_count; a++)
    { var foo ='input' + a;
      var target_name = document.getElementById(foo);
      var target_id   = target_name.id;

      if(target_name) {
        if(a==0)
         target_name.style.display='inline';
        else
         target_name.style.display='None';
      }
    }
  }

   /* selected_search_column.style.visibility=(select.options[select.selectedIndex].value == )?'visible':'hidden'; */
}

function getTop(MyObject)
    {
    if (MyObject.offsetParent)
        return (MyObject.offsetTop + getTop(MyObject.offsetParent));
    else
        return (MyObject.offsetTop);
    }

function loadDivSize () {
var left  = document.getElementById("div_prev");
var right = document.getElementById("div_next");
var sc    = document.getElementById("div_sc");
var good_top = getTop(left);
right.style.top = good_top;
sc.style.top = good_top;
}

function fixLeftRightHeight(){
  var lh = 0;
  var lfieldset;
  var rh = 0;
  var rfieldset;
  var liste=document.getElementsByTagName('fieldset');
  for(i=0; i<liste.length; i=i+1){
    list_parts = liste[i].id.split('_');
    for(j=1; j<list_parts.length; j=j+1){
      if(list_parts[j] == "left"){
        lfieldset = liste[i];
      	lh = lfieldset.offsetHeight;
        break;
      }else{
      	if(list_parts[j] == "right"){
	  rfieldset = liste[i];
	  rh = rfieldset.offsetHeight;
          break;
	}
      }
    }
    if(lh && rh){
      break;
    }
  }
  if(lh && rh){
    lfieldset.style.height=(lh>rh)? lh+"px" : rh+"px";
    rfieldset.style.height=(lh>rh)? lh+"px" : rh+"px";
    lfieldset.style.borderTop = '1px solid #3D7474';
    lfieldset.style.borderLeft = '1px solid #3D7474';
    lfieldset.style.borderBottom = '1px solid #3D7474';
    rfieldset.style.borderTop = '1px solid #3D7474';
    rfieldset.style.borderRight = '1px solid #3D7474';
    rfieldset.style.borderBottom = '1px solid #3D7474';
  }
}
