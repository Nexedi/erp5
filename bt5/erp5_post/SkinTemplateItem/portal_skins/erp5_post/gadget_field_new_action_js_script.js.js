/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("createDocument", function (options) {
      var gadget = this,
        doc = {
          title: "Untitled Document",
          portal_type: options.portal_type,
          parent_relative_url: options.parent_relative_url
        },
        key,
        doc_key;
      for (key in options) {
        if (options.hasOwnProperty(key)) {
          if (key.startsWith("my_")) {
            doc_key = key.replace("my_", "");
            doc[doc_key] = options[key];
          }
        }
      }
      return gadget.jio_post(doc);
    })

    .declareMethod("render", function (parent_options, action_reference, form_definition) {
      var gadget = this;
      return gadget.changeState({
        doc: {title: "Untitled Document"},
        parent_options: parent_options,
        child_gadget_url: 'gadget_erp5_pt_form_dialog.html',
        form_type: 'dialog',
        form_definition: form_definition,
        view: action_reference,
        editable: true,
        has_more_views: false,
        has_more_actions: true
      });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.declareGadget("gadget_officejs_form_view.html")
      .push(function (form_view_gadget) {
        return form_view_gadget.renderGadget(gadget);
      });
    })

    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (gadget) {
          return gadget.triggerSubmit();
        });
    })

    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        jio_key = options[0],
        //target_url = options[1],
        content_dict = options[2],
        document = {
        portal_type: gadget.state.parent_options.portal_type,
        parent_relative_url: gadget.state.parent_options.parent_relative_url,
        my_source_reference: gadget.state.parent_options.my_source_reference
      }, property;
      delete content_dict.dialog_method;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document['my_' + property] = content_dict[property];
        }
      }
      return this.createDocument(document)
      .push(function (id) {
        jio_key = id;
        return gadget.notifySubmitting();
      })
      .push(function () {
        return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
      })
      .push(function () {
        return gadget.redirect({
          command: 'display',
          options: {
            jio_key: jio_key,
            editable: true
          }
        });
      });
    });

}(window, rJS, RSVP));