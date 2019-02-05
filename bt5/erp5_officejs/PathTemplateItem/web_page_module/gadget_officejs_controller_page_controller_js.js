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
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getFormDefinition", function () {
      //somehow the form_definition should come from the erp5-doc/form (jio?)
      //for now, hardcoded form_definition for POST VIEW
      return {
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
      };
    })

    .declareMethod("generateJsonRenderForm", function (form_definition, document) {
      var form_json = {
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
          if (document && document.hasOwnProperty(element_id)) {
            field_info["default"] = document[element_id];
          }
          form_json.erp5_document._embedded._view[my_element] = field_info;
          form_json.erp5_document._links = form_definition._links;
        }
      }
      return form_json;
    })

    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .allowPublicAcquisition('updateDocument', function (param_list) {
      var gadget = this, content = param_list[0];
      return gadget.jio_get(gadget.state.jio_key)
        .push(function (doc) {
          var property;
          for (property in content) {
            if (content.hasOwnProperty(property)) {
              doc[property] = content[property];
            }
          }
          return gadget.jio_put(gadget.state.jio_key, doc);
        });
    })
    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (g) {
          return g.triggerSubmit();
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        child_gadget_url;
      return gadget.jio_get(options.jio_key)
        .push(function (result) {
          if (result.portal_type !== undefined) {
            child_gadget_url = 'gadget_officejs_jio_' +
              result.portal_type.replace(/ /g, '_').toLowerCase() +
              '_view.html';
          } else {
            throw new Error('Can not display document: ' + options.jio_key);
          }
          //somehow the form_definition should come from the erp5-doc/form (jio?)
          return gadget.getFormDefinition(options.jio_key)
            .push(function (form_definition) {
              return gadget.changeState({
                jio_key: options.jio_key,
                doc: result,
                child_gadget_url: child_gadget_url,
                form_definition: form_definition
              });
            });
        });
    })
    .onStateChange(function (modification_dict) {
      var fragment = document.createElement('div'),
        gadget = this;
      return gadget.generateJsonRenderForm(gadget.state.form_definition, gadget.state.doc)
        .push(function (form_json) {
          if (!modification_dict.hasOwnProperty('child_gadget_url')) {
            return gadget.getDeclaredGadget('fg')
              .push(function (child_gadget) {
                return child_gadget.render({
                  jio_key: gadget.state.jio_key,
                  doc: gadget.state.doc,
                  form_json: form_json
                });
              });
          }
          // Clear first to DOM, append after to reduce flickering/manip
          while (gadget.element.firstChild) {
            gadget.element.removeChild(gadget.element.firstChild);
          }
          gadget.element.appendChild(fragment);

          return gadget.declareGadget(gadget.state.child_gadget_url, {element: fragment,
                                                                      scope: 'fg'})
            .push(function (form_gadget) {
              return form_gadget.render({
                jio_key: gadget.state.jio_key,
                doc: gadget.state.doc,
                form_json: form_json
              });
            });
        });
    });

}(document, window, rJS));