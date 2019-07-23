/*global document, window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        default_view,
        app_view,
        form_definition,
        gadget_util,
        jio_document,
        portal_type,
        front_page;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.declareGadget("gadget_officejs_common_util.html"),
            gadget.getSetting('app_view_reference'),
            gadget.getSetting('default_view_reference'),
            gadget.getSetting('documents_editable')
          ]);
        })
        .push(function (result_list) {
          gadget_util = result_list[0];
          app_view = options.action || result_list[1];
          default_view = result_list[2];
          options.editable = ((result_list[3] == "1") ?
                              true : options.editable);
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
            return gadget.getSetting('parent_portal_type');
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
          front_page = portal_type === parent_portal_type;
          return gadget_util.getFormDefinition(portal_type, app_view);
        })
        .push(function (result) {
          return result;
        }, function (error) {
          if (error.status_code === 400) {
            return gadget_util.getFormDefinition(portal_type, default_view);
          }
          throw error;
        })
        .push(function (result) {
          form_definition = result;
          return gadget_util.getFormInfo(form_definition);
        })
        .push(function (form_info) {
          var form_type = form_info[0],
            child_gadget_url = form_info[1];
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: jio_document,
            portal_type: portal_type,
            child_gadget_url: child_gadget_url,
            form_definition: form_definition,
            form_type: form_type,
            editable: options.editable,
            view: options.view || default_view,
            front_page: front_page
          });
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);
      return gadget.declareGadget("gadget_officejs_form_view.html",
                                  {element: fragment, scope: 'form_view'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
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

}(document, window, rJS, RSVP));