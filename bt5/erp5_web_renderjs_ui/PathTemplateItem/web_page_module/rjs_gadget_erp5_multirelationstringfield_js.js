/*jslint indent: 2, maxerr: 3, nomen: true, unparam: true, maxlen: 80 */
/*global window, rJS, RSVP, document */
(function (window, rJS, RSVP, document) {
  "use strict";

  function addRelationInput(gadget, value_relative_url, value_text,
                            value_uid, value_portal_type, index) {
    var input_gadget;
    return gadget.declareGadget('gadget_erp5_relation_input.html', {
      element: document.createElement("fieldset")
    })
      .push(function (result) {
        input_gadget = result;
        return input_gadget.render({
          editable: gadget.state.editable,
          query: gadget.state.query,
          sort_list_json: gadget.state.sort_list_json,
          catalog_index: gadget.state.catalog_index,
          allow_jump: gadget.state.allow_jump,
          // required: field_json.required,
          title: gadget.state.title,
          key: gadget.state.key,
          view: gadget.state.view,
          search_view: gadget.state.search_view,
          url: gadget.state.url,
          allow_creation: gadget.state.allow_creation,
          portal_types: gadget.state.portal_types,
          translated_portal_types: gadget.state.translated_portal_types,
          value_relative_url: value_relative_url,
          value_text: value_text,
          value_uid: value_uid,
          value_portal_type: value_portal_type,
          relation_index: index,
          hidden: gadget.state.hidden
        });
      })
      .push(function () {
        gadget.element.appendChild(input_gadget.element);
      });
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          editable: field_json.editable,
          query: field_json.query,
          sort_list_json: JSON.stringify(field_json.sort),
          catalog_index: field_json.catalog_index,
          allow_jump: field_json.allow_jump,
          required: field_json.required,
          title: field_json.title,
          key: field_json.key,
          view: field_json.view,
          search_view: field_json.search_view,
          url: field_json.url,
          allow_creation: field_json.allow_creation,
          portal_types: field_json.portal_types,
          translated_portal_types: field_json.translated_portal_types,
          relation_field_id: field_json.relation_field_id,
          hidden: field_json.hidden,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };

      if (field_json.default.hasOwnProperty('value_text_list')) {
        //load non saved value
        state_dict.value_relative_url_list =
          JSON.stringify(field_json.default.value_relative_url_list);
        state_dict.value_text_list =
          JSON.stringify(field_json.default.value_text_list);
        state_dict.value_uid_list =
          JSON.stringify(field_json.default.value_uid_list);
        state_dict.value_portal_type_list =
          JSON.stringify(field_json.default.value_portal_type_list);
      } else {
        state_dict.value_relative_url_list =
          JSON.stringify(field_json.relation_item_relative_url);
        state_dict.value_text_list =
          JSON.stringify(field_json.default);
        state_dict.value_uid_list = JSON.stringify([]);
        state_dict.value_portal_type_list = JSON.stringify([]);
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var gadget = this,
        i,
        queue = new RSVP.Queue(),
        element = gadget.element,
        value_relative_url_list =
          JSON.parse(gadget.state.value_relative_url_list),
        value_text_list =
          JSON.parse(gadget.state.value_text_list),
        value_uid_list =
          JSON.parse(gadget.state.value_uid_list),
        value_portal_type_list =
          JSON.parse(gadget.state.value_portal_type_list);


      // Always display an empty value at the end
      value_relative_url_list.push("");
      value_text_list.push("");

      // Clear first to DOM, append after to reduce flickering/manip
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }

      function enQueue() {
        var argument_list = arguments;
        queue
          .push(function () {
            return addRelationInput.apply(this, argument_list);
          });
      }

      for (i = 0; i < value_relative_url_list.length; i += 1) {
        enQueue(gadget, value_relative_url_list[i], value_text_list[i],
                value_uid_list[i], value_portal_type_list[i], i);
      }
      return queue;
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .allowPublicAcquisition('notifyChange', function (argument_list, scope) {
      // An empty relation should be created when the last one is modified
      // An empty relation should be removed

      var gadget = this,
        sub_gadget;
      return gadget.getDeclaredGadget(scope)
        .push(function (result) {
          sub_gadget = result;
          return sub_gadget.getContent();
        })
        .push(function (result) {
          var value = result.value_text;
          if (sub_gadget.element === gadget.element.lastChild) {
            if (value) {
              return addRelationInput(gadget, '', '', undefined, undefined,
                                      gadget.element.childNodes.length);
            }
          /*
          } else {
            if (!value) {
              gadget.element.removeChild(sub_gadget.element);
            }
          */
          }
        })
        .push(function () {
          return gadget.notifyChange();
        });
    })

    .declareMethod('getContent', function (options) {
      var i,
        element = this.element,
        queue = new RSVP.Queue(),
        final_result = {},
        result_list = [],
        gadget = this;

      function calculateSubContent(node) {
        queue
          .push(function () {
            var scope = node.getAttribute('data-gadget-scope');
            if (scope !== null) {
              return gadget.getDeclaredGadget(
                node.getAttribute('data-gadget-scope')
              )
                .push(function (result) {
                  return result.getContent();
                })
                .push(function (result) {
                  result_list.push(result);
                });
            }
          });
      }

      if (this.state.editable) {
        for (i = 0; i < element.childNodes.length; i += 1) {
          calculateSubContent(element.childNodes[i]);
        }
        return queue
          .push(function () {

            var result = {},
              j,
              k = 0,
              input_result;

            if (options.format === "erp5") {
              result[gadget.state.key] = [];
            } else {
              result[gadget.state.key] = {
                value_text_list: [],
                value_relative_url_list: [],
                value_portal_type_list: [],
                value_uid_list: []
              };
            }
            for (j = 0; j < result_list.length; j += 1) {
              input_result = result_list[j];

              if (options.format === "erp5") {
                if (input_result.hasOwnProperty('value_text')) {
                  if (input_result.value_text) {
                    if (input_result.value_portal_type) {
                      result[gadget.state.relation_field_id + '_' + k] =
                        "_newContent_" + input_result.value_portal_type;
                    } else if (input_result.value_uid) {
                      result[gadget.state.relation_field_id + '_' + k] =
                        input_result.value_uid;
                    }
                    result[gadget.state.key].push(input_result.value_text);
                  }
                }
                k += 1;
              } else {
                result[gadget.state.key].value_text_list
                  .push(input_result.value_text);
                result[gadget.state.key].value_relative_url_list
                  .push(input_result.value_relative_url);
                result[gadget.state.key].value_portal_type_list
                  .push(input_result.value_portal_type);
                result[gadget.state.key].value_uid_list.push(undefined);
              }
            }
            //user remove all data
            if (options.format === "erp5" &&
                result[gadget.state.key].length === 0) {
              result[gadget.state.key] = "";
            }
            return result;

          });
      }
      return final_result;
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      var context = this;

      function checkSubContentValidity(node) {
        var scope = node.getAttribute('data-gadget-scope');
        if (scope !== null) {
          return context.getDeclaredGadget(
            node.getAttribute('data-gadget-scope')
          )
            .push(function (result) {
              return result.checkValidity();
            });
        }
      }

      if (this.state.editable) {
        return new RSVP.Queue()
          .push(function () {
            var promise_list = [],
              i;
            for (i = 0; i < context.element.childNodes.length; i += 1) {
              promise_list.push(
                checkSubContentValidity(context.element.childNodes[i])
              );
            }
            return RSVP.all(promise_list);
          })
          .push(function (validity_list) {
            var i;
            for (i = 0; i < validity_list.length; i += 1) {
              if (!validity_list[i]) {
                return false;
              }
            }
            return true;
          });
      }
      return true;

    }, {mutex: 'changestate'});

}(window, rJS, RSVP, document));
