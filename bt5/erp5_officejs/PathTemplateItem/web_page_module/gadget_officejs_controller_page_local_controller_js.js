/*global document, window, rJS, jIO, console */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, jIO, console) {
  "use strict";

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
    .declareAcquiredMethod("updatePanel", "updatePanel")

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
        default_view,
        app_action_list,
        form_definition,
        current_version,
        configurator,
        index;
      current_version = window.location.href.replace(window.location.hash, "");
      index = current_version.indexOf(window.location.host) +
        window.location.host.length;
      current_version = current_version.substr(index);
      return gadget.getSettingList(["migration_version",
                                    "app_view_reference",
                                    "parent_portal_type",
                                    'default_view_reference',
                                    'app_actions',
                                    'app_configurator'])
        .push(function (setting_list) {
          app_view = options.action || setting_list[1];
          parent_portal_type = setting_list[2];
          default_view = setting_list[3];
          app_action_list = setting_list[4];
          configurator = setting_list[5] || 'ojs_configurator';
          if (setting_list[0] !== current_version) {
            //if app version has changed, force storage selection
            return gadget.redirect({
              'command': 'display',
              'options': {
                'page': configurator,
                'auto_repair': true
              }
            });
          }
        })
        .push(function () {
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
          form_definition = result;
          return gadget_util.getViewAndActionDict(portal_type, app_view,
                                                  default_view, app_action_list,
                                                  options.jio_key);
        })
        .push(function (view_action_dict) {
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: jio_document,
            portal_type: portal_type,
            child_gadget_url: form_definition.child_gadget_url,
            form_definition: form_definition,
            form_type: form_definition.form_type,
            view: options.view || app_view,
            view_action_dict: view_action_dict
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
    }, {mutex: 'render'})

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this,
        view_gadget_url = "gadget_officejs_form_view.html",
        //TODO: this should be a list, not only one custom view
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
                                  {element: fragment,
                                   scope: 'officejs_form_view'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        })
        .push(function () {
          return gadget.updatePanel({
            view_action_dict: gadget.state.view_action_dict
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
      return this.getDeclaredGadget('officejs_form_view')
        .push(function (view_gadget) {
          return view_gadget.triggerSubmit(argument_list);
        });
    }, {mutex: 'render'});

}(document, window, rJS, jIO, console));