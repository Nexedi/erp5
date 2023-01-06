/*global document, window, rJS, jIO, console */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, jIO, console) {
  "use strict";

  rJS(window)
    .ready(function () {
      this._debug = 'ready\n';
    })

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
      this._debug += 'render starting\n';

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
        index;
      current_version = window.location.href.replace(window.location.hash, "");
      index = current_version.indexOf(window.location.host) +
        window.location.host.length;
      current_version = current_version.substr(index);
      gadget._debug += 'render ongoing\n';
      return gadget.getSettingList(["migration_version",
                                    "app_view_reference",
                                    "parent_portal_type",
                                    'default_view_reference',
                                    'app_actions'])
        .push(function (setting_list) {
          gadget._debug += 'render setting list fetched\n';

          app_view = options.action || setting_list[1];
          parent_portal_type = setting_list[2];
          default_view = setting_list[3];
          app_action_list = setting_list[4];
          if (setting_list[0] !== current_version) {
            //if app version has changed, force storage selection
            gadget._debug += 'render want to redirect\n';

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
          gadget._debug += 'render get common list\n';

          return gadget.getDeclaredGadget("common_util");
        })
        .push(function (result) {
          gadget._debug += 'render common list fetched\n';

          gadget_util = result;
          console.log('common util', gadget_util);
          return gadget.jio_get(options.jio_key);
        })
        .push(function (result) {
          gadget._debug += 'render jio key fetched\n';

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
          gadget._debug += 'render before getformdefinition\n';

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
          gadget._debug += 'render before getviewandactiondict\n';

          form_definition = result;
          return gadget_util.getViewAndActionDict(portal_type, app_view,
                                                  default_view, app_action_list,
                                                  options.jio_key);
        })
        .push(function (view_action_dict) {
          gadget._debug += 'render before changeState\n';

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
        })
        .push(function (result) {
          gadget._debug += 'render ending\n';
          return result;
        }, function (error) {
          gadget._debug += 'render error\n' + error + '\n';
          throw error;
        });
    }, {mutex: 'render'})

    .onStateChange(function () {
      this._debug += 'onStateChange starting\n';

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
                                  {element: fragment,
                                   scope: 'officejs_form_view'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        }, function (error) {
          console.log(error);
          return gadget.notifySubmitted({
            message: "Error rendering view",
            status: "error"
          });
        })
        .push(function () {
          return gadget.updatePanel({
            view_action_dict: gadget.state.view_action_dict
          });
        })
        .push(function (result) {
          gadget._debug += 'onStateChange stopping\n';
          return result;
        }, function (error) {
          gadget._debug += 'onstatechange error\n' + error + '\n';
          throw error;
        });
    })

    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .allowPublicAcquisition('submitContent', function (param_list) {
      this._debug += 'submitContent starting\n';

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
        })
        .push(function (result) {
          gadget._debug += 'submitContent stopping\n';
          return result;
        }, function (error) {
          gadget._debug += 'submitContent error\n' + error + '\n';
          throw error;
        });
    })

    .declareMethod("triggerSubmit", function () {
      this._debug += 'triggerSubmit starting\n';
      var argument_list = arguments,
        gadget = this;
      return this.getDeclaredGadget('officejs_form_view')
        .push(function (view_gadget) {
          return view_gadget.triggerSubmit(argument_list);
        }, function (error) {
          throw new Error('Failed getting officejs_form_view.\n' + gadget._debug);
        })
        .push(function (result) {
          gadget._debug += 'triggerSubmit stopping\n';
          return result;
        }, function (error) {
          gadget._debug += 'triggerSubmit error\n' + error + '\n';
          throw error;
        });

    }, {mutex: 'render'});

}(document, window, rJS, jIO, console));