/*global document, window, rJS, RSVP, jIO, console */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP, jIO, console) {
  "use strict";

  var warmup_gadget_done = false,
    warmup_list = [
      //officejs gadgets
      'gadget_officejs_form_view.html',
      'gadget_officejs_common_util.html',
      'gadget_erp5_label_field.html',
      'gadget_html5_element.html',
      'gadget_erp5_field_datetime.html',
      'gadget_erp5_field_string.html',
      'gadget_erp5_form.html',
      'gadget_erp5_field_float.html',
      'gadget_erp5_field_listbox.html',
      // Used in panel
      'gadget_translation.html',
      'gadget_erp5_panel.html',
      'gadget_erp5_header.html',
      'gadget_erp5_searchfield.html',
      'gadget_erp5_field_multicheckbox.html',
      'gadget_html5_input.html',
      //following elements should be split in at list 2 groups (doclist and doc)
      'gadget_erp5_pt_form_list',
      'gadget_erp5_pt_form_view.html',
      //
      'gadget_erp5_pt_form_view_editable.html',
      'gadget_erp5_field_textarea.html',
      'gadget_erp5_field_gadget.html',
      'gadget_html5_textarea.html',
      'gadget_editor.html'
    ];

  function warmupGadgetList(gadget, url_list) {
    var i;
    for (i = 0; i < url_list.length; i += 1) {
      // No need to check the result, as it will fail later
      // when rJS will try to instanciate one of this gadget
      rJS.declareGadgetKlass(rJS.getAbsoluteURL(url_list[i],
                                                gadget.__path));
    }
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        app_view,
        gadget_util,
        jio_document,
        portal_type,
        parent_portal_type,
        current_version,
        index;
      current_version = window.location.href.replace(window.location.hash, "");
      index = current_version.indexOf(window.location.host) +
        window.location.host.length;
      current_version = current_version.substr(index);
      return gadget.getSettingList(["migration_version",
                                    "app_view_reference",
                                    "parent_portal_type"])
        .push(function (setting_list) {
          app_view = options.action || setting_list[1];
          parent_portal_type = setting_list[2];
          if (setting_list[0] !== current_version) {
            //if app version has changed, force storage selection
            return gadget.redirect({
              'command': 'display',
              'options': {
                'page': 'ojs_configurator',
                'auto_repair': true
              }
            });
          }
        })
        .push(function () {
          if (!warmup_gadget_done) {
            warmupGadgetList(gadget, warmup_list);
            warmup_gadget_done = true;
          }
          return gadget.getDeclaredGadget("common_util");
        })
        .push(function (result) {
          gadget_util = result;
          return gadget.jio_get(options.jio_key);
        })
        .push(function (result) {
          jio_document = result;
          if (jio_document.portal_type === undefined) {
            throw new Error('Can not display document: ' + options.jio_key);
          }
        }, function (error) {
          // instaceof error is Object, so use status_code and undefined jio_key
          if (error.status_code === 400 && !options.jio_key) {
            return parent_portal_type;
          }
          throw error;
        })
        .push(function (parent_portal_type) {
          if (jio_document) {
            portal_type = jio_document.portal_type;
          } else if (options.portal_type) {
            portal_type = options.portal_type;
          } else {
            portal_type = parent_portal_type;
          }
          return gadget_util.getFormDefinition(portal_type, app_view);
        })
        .push(function (result) {
          return result;
        })
        .push(function (form_definition) {
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: jio_document,
            portal_type: portal_type,
            child_gadget_url: form_definition.child_gadget_url,
            form_definition: form_definition,
            form_type: form_definition.form_type,
            view: options.view || app_view
          });
        }, function (error) {
          // jio not found error
          if ((error instanceof jIO.util.jIOError) &&
              (error.status_code === 404)) {
            console.log(error);
            return gadget.notifySubmitted({
              message: error.message + ". Maybe syncronize?",
              status: "error"
            });
          }
          throw error;
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this,
        view_gadget_url = "gadget_officejs_form_view.html",
        custom_gadget_url = gadget.state.form_definition.portal_type_dict
          .custom_view_gadget;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      if (custom_gadget_url) {
        view_gadget_url = custom_gadget_url;
      }
      gadget.element.appendChild(fragment);
      return gadget.declareGadget(view_gadget_url,
                                  {element: fragment, scope: 'form_view'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        }, function (error) {
          console.log(error);
          return gadget.notifySubmitted({
            message: "Error rendering view",
            status: "error"
          });
        });
    })

    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .allowPublicAcquisition('submitContent', function (param_list) {
      var gadget = this,
        //target_url = options[1],
        content_dict = param_list[2];
      return gadget.jio_get(gadget.state.jio_key)
        .push(function (doc) {
          var property;
          for (property in content_dict) {
            if (content_dict.hasOwnProperty(property)) {
              doc[property] = content_dict[property];
            }
          }
          return gadget.jio_put(gadget.state.jio_key, doc);
        })
        .push(function () {
          return gadget.notifySubmitting();
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated',
                                         status: 'success'});
        });
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_view')
        .push(function (view_gadget) {
          return view_gadget.triggerSubmit(argument_list);
        });
    });

}(document, window, rJS, RSVP, jIO, console));