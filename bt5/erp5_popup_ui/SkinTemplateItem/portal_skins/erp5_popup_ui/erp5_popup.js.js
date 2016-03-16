/*
Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
                   Yoshinori Okuji <yo@nexedi.com>

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
Note: this JavaScript is used to pop up dialogs inside the same pages, instead of transiting into different pages.
It would not be difficult to extend this script to support more types of dialogs, but it is enabled only for
relation update dialogs at the moment. This is tested with erp5_xhtml_style.

If you want to use this feature, you need to load additional files in global_definitions:

           dummy                python:js_list.extend(('%s/jquery-ui-1.7.2/js/jquery-1.3.2.min.js' % portal_path, '%s/jquery-ui-1.7.2/js/jquery-ui-1.7.2.custom.min.js' % portal_path));
           dummy                python:css_list.append('%s/jquery-ui-1.7.2/css/erp5-theme/jquery-ui-1.7.2.custom.css' % portal_path);
           dummy                python:js_list.append('%s/erp5_popup.js' % portal_path);

The first two lines are required for loading jQuery and jQuery UI. The last line is for this file.
*/

$(function() {
  /*
   * generic dialog to display another ERP5 page on top of the page.
   *
   * Parameters:
   * 'dialog': object to pass as argument to $.ui.dialog on creation.
   *           erp5_dialog has generic defaults, and everything you will
   *           pass will override those defaults.
   * 'load'  :
   *        - url: url to load in the popup
   *        - params: parameters to give to the ajax call. can be omitted
   *        - method: default $.post, you can change it to $.get
   *
   * Example:
   *   $('<div id="jquery_erp5_dialog" />').appendTo('body').erp5_popup({
   *        dialog: {title: 'It works', },
   *        load: {url: '/erp5/some_module/someobject'},
   *   )};
   */
  $.fn.erp5_popup = function(params) {
    dialog = $(this);

    var default_dialog_parameters = {
       modal: true,
       width: $(window).width() * 0.8,
       height: $(window).height() * 0.8,
       title: 'ERP5 dialog',
       close: function() {
         dialog.dialog('destroy');
         dialog.empty();
      },
    }
    // initalize jQuery dialog
    dialog.dialog($.extend({}, default_dialog_parameters, params.dialog));

    var load = function(url, query, ajax_method) {
      if (!query) query = {};
      if (!ajax_method) ajax_method = $.post;
      //dialog.empty();
      // scroll up to begin of "window"
      window.scrollTo(0,0);
      // Some bogus animations for having the user to feel easier.
      var animate = function() {
        var element = $('p.loading', dialog);
        if (element.length != 0) {
          //element.animate({opacity: 1}, 2000, 'linear');
          //element.animate({opacity: 0}, 2000, 'linear', animate);
          element.animate({color: 'white'}, 2000, 'linear');
          element.animate({color: 'black'}, 2000, 'linear', animate);
        }
      };
      $('<div class="loading" style="background-color: #AAAAAA; opacity: 0.5; position: absolute; left: 0%; width: 100%; top: 0%; height: 100%; transparent;"><p class="loading" style="position: absolute; left: 0%; width: 100%; top: 30%; height: 40%; text-align: center; color: black; font-size: 32pt;">Loading...</p></div>').appendTo(dialog);
      animate();

      ajax_method(url, query, function(data, textStatus, XMLHttpRequest) {
        if (textStatus == 'success' || textStatus == 'notmodified') {
          // Stop the animations above.
          dialog.empty();
          //$('div.loading', dialog).remove();

          dialog.html($('<div />').append(data.replace(/<script(.|\s)*?\/script>/g, '')).find('form'));

          // XXX Get rid of unneeded stuff in JavaScript for now.
          $('.bars, .breadcrumb, .logged_in_as', dialog).remove();
          $('[id]', dialog).removeAttr('id');
          // XXX Get rid of unneeded KM stuff in JavaScript for now.
          $('.wrapper', dialog).remove();

          // Insert the same buttons as at the bottom into near the top.
          //$('div.bottom_actions', dialog).clone().insertAfter($('div.dialog_box', dialog)).css('margin-bottom', '1em');

          $('input[type="image"], button.sort_button, .dialog_selector > button, button.save', dialog).click(function(event) {
            event.preventDefault();
            var self = $(this);
            var form = $('form.main_form', dialog);
            var params = {};
            params[self.attr('name')] = self.attr('value');
            load(form.attr('action'), $.param(params) + '&' + form.serialize());
          });

          // XXX Remove the hardcoded handler.
          $('.dialog_selector > select[onchange]', dialog).removeAttr('onchange');
          $('.dialog_selector > select', dialog).change(function(event) {
            //event.preventDefault();
            var button = $('button', this.parentNode);
            var form = $('form.main_form', dialog);
            var params = {};
            params[button.attr('name')] = button.attr('value');
            load(form.attr('action'), $.param(params) + '&' + form.serialize());
          });

          // listbox type in page number
          $('input[name="listbox_page_start"][onkeypress]', dialog).removeAttr('onkeypress');
          $('input[name="listbox_page_start"]', dialog).keypress(function(event) {
            if (event.keyCode == '13') {
              event.preventDefault();
              var self = $(this);
              self.value = self.attr('defaultValue');
              var form = $('form.main_form', dialog);
              // XXX no other way but hardcoding the method name.
              load('listbox_setPage', form.serialize());
            }
          });
          
          // Listbox next & previous, last & first buttons
          $.each(['listbox_nextPage', 'listbox_previousPage', 'listbox_firstPage', 'listbox_lastPage'], 
                 function(index, value) {
                   var button = $('button[type="submit"][name="' + value + ':method"]', dialog).first();
                   button.click(function(event) {
                                  var form = $('form.main_form', dialog);
                                  event.preventDefault();
                                  load(value, form.serialize());            
                   });
          });
         
          $('th.listbox-table-filter-cell input[type="text"]', dialog).removeAttr('onkeypress').keypress(function(event) {
            if (event.keyCode == '13') {
              event.preventDefault();
              //var self = $(this);
              //self.value = self.attr('defaultValue');
              var form = $('form.main_form', dialog);
              var first_submit_button = $($('input[type="submit"]', form)[0]);
              var params = {};
              params[first_submit_button.attr('name')] = first_submit_button.attr('value');
              load(form.attr('action'), $.param(params) + '&' + form.serialize());
            }
          });

          $('button.dialog_cancel_button', dialog).click(function(event) {
            event.preventDefault();
            dialog.dialog('close');
          });

          $('button.dialog_update_button', dialog).click(function(event) {
            event.preventDefault();
            var self = $(this);
            var form = $('form.main_form', dialog);
            var params = {};
            params[self.attr('name')] = self.attr('value');
            load(form.attr('action'), $.param(params) + '&' + form.serialize());
          });
        }
      });
    };
    load(params.load.url, params.load.params, params.load.method);
  };
});

$(function() {
  // XXX It is necessary to keep a reference to a dialog, because jQuery / jQuery UI does not keep information
  // in elements of DOM unfortunately. This is not a big problem at the moment, because this implementation assumes
  // that a dialog is modal.
  // XXX Nicolas: see $.data() for storage in DOM. I dont think that it matters however. $("#jquery_erp5_dialog") should be enough
  var dialog = $('<div id="jquery_erp5_dialog" />').appendTo('body');


  // Those two definitions could be kept in a different file. The jQuery plugin providing an implementation is different than
  // the places where we use this plugin

  // Make the relation update dialogs as pop-ups.
  $('input[value="update..."]').click(function(event) {
    event.preventDefault();

    var self = $(this);
    var form = $('form#main_form');
    var params = {};
    params[self.attr('name')] = self.attr('value');

    dialog.erp5_popup({
        dialog: { title: $('label', this.parentNode.parentNode).text() },
        load: {
            url: form.attr('action'),
            params: $.param(params) + '&' + form.serialize(),
        }
    });
  });
  
  // login logout links for KM
  $('a[id="login-logout-link"]').click(function(event) {
    if($('a[id="login-logout-link"]').attr('href').indexOf('login_form')==-1){
      // we show popup only for login_form
      return
    }
    event.preventDefault();

    dialog.erp5_popup({
        dialog: { title: $('label', this.parentNode.parentNode).text() },
        load: {
            url: this.href,
            method: $.get,
        }
    });
  });
  
  
  // Make the Add gadget dialog work as pop-ups.
  $('a[id="add-gadgets"]').click(function(event) {
    event.preventDefault();

    dialog.erp5_popup({
        dialog: { title: $('label', this.parentNode.parentNode).text() },
        load: {
            url: this.href,
            method: $.get,
        }
    });
  });

});
