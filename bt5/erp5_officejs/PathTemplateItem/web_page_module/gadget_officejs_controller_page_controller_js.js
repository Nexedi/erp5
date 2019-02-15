/*global document, window, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP, jIO) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getFormDefinition", function () {
      //preparing a less hardcoded version, moving form definition to erp5 side
      /*var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('hateoas_url'),
            gadget.getSetting('default_view_reference')
          ]);
        })
        .push(function (setting_list) {
          var jio_options = {
            type: "erp5",
            url: setting_list[0],
            default_view_reference: setting_list[1]
          },
          jio_storage = jIO.createJIO(jio_options);
          return jio_storage.get('portal_skins/erp5_officejs_jio_connector/HTMLPost_viewAsJio')
            .push(function (result) {
              return result.form_definition;
            });
        });*/
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
        _links: { "type": { name: "" } },
        _actions: { "put": true }
      };
    })

    .declareMethod("generateJsonRenderForm", function (form_definition, document) {
      var form_json = {
        erp5_document: {
          "_embedded": {"_view": {}},
          "_links": {}
        },
        form_definition: form_definition
      }, i, j, fields, field_info, my_element, element_id;
      for (i = 0; i < form_definition.group_list.length; i += 1) {
        fields = form_definition.group_list[i][1];
        for (j = 0; j < fields.length; j += 1) {
          my_element = fields[j][0];
          if (my_element.startsWith("my_")) {
            element_id = my_element.replace("my_", "");
          } else if (my_element.startsWith("your_")) {
            element_id = my_element.replace("your_", "");
          }
          field_info = form_definition.field_info_dict[my_element];
          if (document && document.hasOwnProperty(element_id)) {
            field_info["default"] = document[element_id];
          }
          form_json.erp5_document._embedded._view[my_element] = field_info;
        }
      }
      form_json.erp5_document._embedded._view._actions = form_definition._actions;
      form_json.erp5_document._links = form_definition._links;
      return form_json;
    })
    .allowPublicAcquisition('submitContent', function (options) {
      var gadget = this,
        jio_key = options[0],
        //target_url = options[1],
        content_dict = options[2];
      return gadget.notifySubmitting()
        .push(function () {
          // this should be jio_getattachment (using target_url)
          return gadget.jio_get(jio_key)
            .push(function (document) {
              var property;
              for (property in content_dict) {
                if (content_dict.hasOwnProperty(property)) {
                  document[property] = content_dict[property];
                }
              }
              return gadget.jio_put(jio_key, document);
            });
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        });
    })
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (gadget) {
          return gadget.triggerSubmit();
        });
    })

    .declareMethod("renderSubGadget", function (gadget, subgadget, form_json) {
      return subgadget.render({
        jio_key: gadget.state.jio_key,
        doc: gadget.state.doc,
        erp5_document: form_json.erp5_document,
        form_definition: form_json.form_definition,
        editable: gadget.state.editable,
        view: gadget.state.view,
        form_json: form_json
      })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (url_list) {
          return subgadget.updateHeader({
            page_title: gadget.state.doc.title,
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        child_gadget_url;
      return gadget.jio_get(options.jio_key)
        .push(function (result) {
          if (result.portal_type !== undefined) {
            /*child_gadget_url = 'gadget_officejs_jio_' +
              result.portal_type.replace(/ /g, '_').toLowerCase() +
              '_view.html';*/
            // [HARDCODED] force to use form view editable
            child_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
          } else {
            throw new Error('Can not display document: ' + options.jio_key);
          }
          return gadget.getFormDefinition(options.jio_key)
            .push(function (form_definition) {
              return gadget.changeState({
                jio_key: options.jio_key,
                doc: result,
                child_gadget_url: child_gadget_url,
                form_definition: form_definition,
                editable: options.editable,
                view: options.view
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
                return gadget.renderSubGadget(gadget, child_gadget, form_json);
              });
          }
          // Clear first to DOM, append after to reduce flickering/manip
          while (gadget.element.firstChild) {
            gadget.element.removeChild(gadget.element.firstChild);
          }
          gadget.element.appendChild(fragment);
          return gadget.declareGadget(gadget.state.child_gadget_url, {element: fragment, scope: 'fg'})
            .push(function (form_gadget) {
              return gadget.renderSubGadget(gadget, form_gadget, form_json);
            });
        });
    });

}(document, window, rJS, RSVP, jIO));