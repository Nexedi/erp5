/*global document, window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        default_view = "jio_view",
        common_utils_gadget_url = "gadget_officejs_common_utils.html",
        form_definition,
        gadget_utils,
        jio_document,
        portal_type,
        front_page;
      return gadget.declareGadget(common_utils_gadget_url)
        .push(function (result) {
          gadget_utils = result;
          return gadget.jio_get(options.jio_key);
        })
        .push(function (result) {
          jio_document = result;
          if (jio_document.portal_type === undefined) {
            throw new Error('Can not display document: ' + options.jio_key);
          }
        }, function (error) {})
        .push(function () {
          return gadget.getSetting('parent_portal_type');
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
          return gadget_utils.getFormDefinition(portal_type, default_view);
        })
        .push(function (result) {
          form_definition = result;
          //TODO: solve add button (header add button - '+' icon)
          //solved: add elements must be done via actions
          /*if (form_definition.action_type === "object_list") {
            form_definition._links.action_object_new_content_action = {
              page: "handle_action",
              title: "New Post",
              action: "new_html_post",
              reference: "new_html_post",
              action_type: "object_jio_js_script",
              parent_portal_type: "Post Module",
              source_reference: "for-future-thread-id"
            };
          }*/
          return gadget_utils.getFormInfo(form_definition);
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
            //TODO editable should come from getFormInfo(form_definition)
            editable: true,
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
      return gadget.declareGadget("gadget_officejs_form_view.html", {element: fragment,
                                                                     scope: 'form_view'})
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
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        });
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_view')
        .push(function (view_gadget) {
          return view_gadget.triggerSubmit(argument_list);
        });
    });

}(document, window, rJS));