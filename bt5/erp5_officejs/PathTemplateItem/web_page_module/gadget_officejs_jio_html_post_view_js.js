/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("generateJsonRenderForm", function (gadget) {
      //hardcoded form_definition (this should come from erp5 form)
      var form_definition = {
        _debug: "traverse",
        pt: "form_view",
        title: "Post",
        group_list: [[
          "left",
          [["my_title", {meta_type: "StringField"}]]
        ], [
          "bottom",
          [["my_text_content", {meta_type: "ProxyField"}]]
        ]],
        //this field_info is totally made up, but somewhere in the definition there must be
        //information about the fields. So, foreach field: key->info
        field_info_dict: {
          "my_title": {
            "title": "Title",
            "default": "Undefined title",
            "editable": 1,
            "key": "title",
            "type": "StringField"
          },
          "my_text_content": {
            "editable": 1,
            "key": "text_content",
            "renderjs_extra": '{"editor": "fck_editor",' +
              '"maximize": true}',
            "type": "GadgetField",
            "url": "gadget_editor.html",
            "sandbox": "public"
          }
        },
        action: "Base_edit",
        update_action: "",
        _links: {}
      },
      form_json = {
        erp5_document: {
          "_embedded": {"_view": {}},
          "_links": {}
        },
        form_definition: form_definition
      };
      for (var i = 0; i < form_definition.group_list.length; i++) {
        var fields = form_definition.group_list[i][1];
        for (var j = 0; j < fields.length; j++) {
          var my_element = fields[j][0], element_id;
          if (my_element.startsWith("my_")) {
            element_id = my_element.replace("my_", "");
          }
          var field_info = form_definition.field_info_dict[my_element];
          if (gadget.state.hasOwnProperty("doc") && gadget.state.doc.hasOwnProperty(element_id)) {
            field_info["default"] = gadget.state.doc[element_id];
          }
          form_json.erp5_document._embedded._view[my_element] = field_info;
          form_json.erp5_document._links = form_definition._links;
        }
      }
      return form_json;
    })

    .declareMethod("render", function (options) {
      return this.changeState({
        jio_key: options.jio_key,
        doc: options.doc
      });
    })

    .onEvent('submit', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          return gadget.updateDocument(content);
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function () {
      var gadget = this,
          form_json;
      return gadget.generateJsonRenderForm(gadget)
        .push(function (result) {
          form_json = result;
          return gadget.getDeclaredGadget('form_view')
            .push(function (form_gadget) {
              return form_gadget.render(form_json);
            })
            .push(function () {
              return RSVP.all([
                gadget.getUrlFor({command: 'history_previous'}),
                gadget.getUrlFor({command: 'selection_previous'}),
                gadget.getUrlFor({command: 'selection_next'})
              ]);
            })
            .push(function (url_list) {
              return gadget.updateHeader({
                page_title: gadget.state.doc.title,
                save_action: true,
                selection_url: url_list[0],
                previous_url: url_list[1],
                next_url: url_list[2]
              });
            });
        });
    });
}(window, rJS, RSVP));
