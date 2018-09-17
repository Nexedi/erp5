/*jslint indent: 2, maxerr: 3, nomen: true, maxlen: 80 */
/*global window, rJS */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var context = this,
        field_json = options.field_json || {};
      return context.getDeclaredGadget("relation_input")
        .push(function (gadget) {
          var render_options = {
            editable: field_json.editable,
            query: field_json.query,
            sort_list_json: JSON.stringify(field_json.sort),
            catalog_index: field_json.catalog_index,
            allow_jump: field_json.allow_jump,
            // required: field_json.required,
            title: field_json.title,
            key: field_json.key,
            view: field_json.view,
            url: field_json.url,
            allow_creation: field_json.allow_creation,
            portal_types: field_json.portal_types,
            translated_portal_types: field_json.translated_portal_types,
            value_relative_url: field_json.relation_item_relative_url[0],
            relation_index: 0,
            hidden: field_json.hidden
          };

          if (field_json.default.hasOwnProperty('value_text_list')) {
            //load non saved value
            render_options.value_relative_url =
              field_json.default.value_relative_url_list[0];
            render_options.value_uid =
              field_json.default.value_uid_list[0];
            render_options.value_text =
              field_json.default.value_text_list[0];
            render_options.value_portal_type =
              field_json.default.value_portal_type_list[0];
          } else {
            render_options.value_text = field_json.default[0] || "";
          }

          return gadget.render(render_options);
        })
        .push(function () {
          return context.changeState({
            key: options.field_json.key,
            relation_field_id: options.field_json.relation_field_id
          });
        });
    })

    .declareMethod('getContent', function (options) {
      var gadget = this;
      return this.getDeclaredGadget("relation_input")
        .push(function (input_gadget) {
          return input_gadget.getContent();
        })
        .push(function (input_result) {
          var result = {};
          if (!input_result.hasOwnProperty('value_text')) {
            return result;
          }
          if (options.format === "erp5") {
            if (input_result.value_portal_type) {
              result[gadget.state.relation_field_id] =
                "_newContent_" + input_result.value_portal_type;
            } else if (input_result.value_uid) {
              result[gadget.state.relation_field_id] =
                input_result.value_uid;
            }
            result[gadget.state.key] = input_result.value_text;
          } else {
            result[gadget.state.key] = {
              value_text_list: [input_result.value_text],
              value_relative_url_list: [input_result.value_relative_url],
              value_portal_type_list: [input_result.value_portal_type],
              value_uid_list: [undefined]
            };
          }
          return result;
        });
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      return this.getDeclaredGadget("relation_input")
        .push(function (input_gadget) {
          return input_gadget.checkValidity();
        });
    }, {mutex: 'changestate'});

}(window, rJS));