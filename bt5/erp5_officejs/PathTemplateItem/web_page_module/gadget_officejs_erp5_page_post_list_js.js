/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        default_view = "jio_view",
        common_utils_gadget_url = "gadget_officejs_common_utils.html",
        child_gadget_url = 'gadget_erp5_pt_form_list.html',
        //HARDCODED NEW ACTION INFORMATION - TODO: get like in action_offline gadget (refactor/reuse code)
        fake_thread_uid = "thread-" + ("0000" + ((Math.random() * Math.pow(36, 4)) | 0).toString(36)).slice(-4),
        action_info = {
          page: "handle_action",
          action: "new",
          portal_type: "HTML Post",
          parent_portal_type: "Post Module",
          my_source_reference: fake_thread_uid
        };
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('parent_portal_type'),
            gadget.declareGadget("gadget_officejs_common_utils.html")
          ]);
        })
        .push(function (result) {
            return result[1].getFormDefinition(result[0], default_view);
          })
          .push(function (form_definition) {
            //HARDCODED ACTION INFORMATION
            form_definition._links.action_object_new_content_action = action_info;
            return gadget.changeState({
              jio_key: options.jio_key,
              child_gadget_url: child_gadget_url,
              form_definition: form_definition,
              form_type: 'list',
              editable: false,
              view: default_view,
              front_page: true,
              has_more_views: false, //this should come from form_def
              has_more_actions: false //this should come from form_def
            });
          });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this,
        options;
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

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_view')
        .push(function (view_gadget) {
          return view_gadget.getDeclaredGadget('fg');
        })
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    });

}(window, document, rJS, RSVP));