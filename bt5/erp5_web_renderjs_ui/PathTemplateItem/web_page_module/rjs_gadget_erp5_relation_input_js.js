/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, URI, loopEventListener, Handlebars,
 SimpleQuery, ComplexQuery, Query, QueryFactory, promiseEventListener, $*/
(function (window, rJS, RSVP, URI, loopEventListener, promiseEventListener,
  SimpleQuery, ComplexQuery, Query, QueryFactory, Handlebars, $) {
  "use strict";


  var gadget_klass = rJS(window),
    relation_input_source = gadget_klass.__template_element
                         .getElementById("relation-input-template")
                         .innerHTML,
    relation_input_template = Handlebars.compile(relation_input_source),

    relation_listview_source = gadget_klass.__template_element
                         .getElementById("relation-listview-template")
                         .innerHTML,
    relation_listview_template = Handlebars.compile(relation_listview_source),


    searching = "ui-btn ui-corner-all ui-btn-icon-notext" +
        " ui-input-clear ui-icon-spinner ui-icon-spin",
    searched = "ui-hidden-accessible",
    jump_on = "ui-btn ui-corner-all ui-btn-icon-notext " +
      "ui-icon-plane ui-shadow-inset ui-btn-inline",
    jump_off = "ui-btn ui-corner-all ui-btn-icon-notext " +
      "ui-icon-plane ui-shadow-inset ui-btn-inline ui-disabled",
    jump_add = "ui-btn ui-corner-all ui-btn-icon-notext " +
      "ui-icon-plus ui-shadow-inset ui-btn-inline ui-disabled",
    jump_unknown = "ui-btn ui-corner-all ui-btn-icon-notext " +
      "ui-icon-warning ui-shadow-inset ui-btn-inline ui-disabled";


  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (my_gadget) {
      my_gadget.props = {};
      return my_gadget.getElement()
        .push(function (element) {
          my_gadget.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getFormContent", "getFormContent")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("addRelationInput", "addRelationInput")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options, options2) {
      var gadget = this,
        field_json = options.field_json || {},
        target_url,
        queue = new RSVP.Queue(),
        create_object,
        unknown,
        relation_item_relative_url,
        uid,
        value = "",
        not_selected = true,
        index = options2.index || 0;
      gadget.props.index = index;
      gadget.props.addRelationInput = options2.addRelationInput;
      if (field_json.default.value) {
        //load non saved value
        create_object =  field_json.default.create_object ? field_json.default.create_object[index] : false;
        unknown = field_json.default.jump_unknown ? field_json.default.jump_unknown[index] : false;
        relation_item_relative_url = field_json.default.relation_item_relative_url || [];
        uid = field_json.default.uid;
        value = field_json.default.value[index] || "";
      } else {
        create_object = field_json.create_object ? field_json.create_object[index] : false;
        unknown = field_json.jump_unknown ? field_json.jump_unknown[index] : false;
        relation_item_relative_url = field_json.relation_item_relative_url;
        uid = field_json.uid;
        value = field_json.default[index] || "";
      }
      gadget.props.jump_url = [relation_item_relative_url[index]];
      if (relation_item_relative_url) {
        target_url = relation_item_relative_url[index];
      }
      gadget.props.field_json = field_json;
      gadget.props.query = QueryFactory.create(new URI(field_json.query).query(true).query);
      gadget.props.create_object_type = create_object;
      if (!value && target_url && uid) {
        //return from listbox
        not_selected = false;
        queue
          .push(function () {
            return gadget.jio_allDocs({
              "query":  Query.objectToSearchText(new SimpleQuery({
                key: "catalog.uid",
                value: uid,
                limit: [0, 1]
              })),
              "select_list": [field_json.catalog_index]
            });
          })
          .push(function (result) {
            value = result.data.rows[0].value[field_json.catalog_index];
          });
      }
      if (target_url) {
        queue
          .push(function () {
            return gadget.getUrlFor({
              command: 'index',
              options: {
                jio_key: target_url
              }
            });
          });
      }
      queue
        .push(function (href) {
          var class_name,
            jump_href = '#';
          if (create_object) {
            class_name = jump_add;
          } else {
            if ((field_json.error_text || unknown) && not_selected) {
              class_name = jump_unknown;
            } else {
              if (href) {
                if (field_json.allow_jump) {
                  jump_href = href;
                  class_name = jump_on;
                } else {
                  class_name = jump_off;
                }
              } else {
                class_name = jump_off;
              }
            }
          }
          return gadget.translateHtml(relation_input_template({
            href: jump_href,
            create_object: create_object,
            readonly: field_json.editable ? "" : "ui-state-readonly",
            required: field_json.required ? "required" : "",
            value: value,
            title: field_json.title,
            name: field_json.key,
            class_name: class_name
          }));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          gadget.props.input =
            gadget.props.element.querySelector("input");
          gadget.props.new_tag_div = gadget.props.element.querySelector(".new_tag");
          gadget.props.spinner = gadget.props.element.querySelector("a");
          gadget.props.plane = gadget.props.element.querySelectorAll("a")[1];
        });
      return queue;
    })
    .declareMethod('getContent', function (options, options2) {
      var element = this.props.element.querySelector('input'),
        result = {},
        tmp = {},
        field_json = this.props.field_json;
      if (options.format === "erp5") {
        if (this.props.plane.className === jump_add) {
          if (options2 && options2.type === 'MultiRelationField') {
            result[field_json.relation_field_id + '_' + this.props.index] = "_newContent_" + this.props.create_object_type;
          } else {
            result[field_json.relation_field_id] = "_newContent_" + this.props.create_object_type;
          }
        }
        result[element.getAttribute('name')] = element.value;
        return result;
      }
      tmp.value = [element.value];
      tmp.create_object = [""];
      tmp.jump_unknown = [""];
      tmp.relation_item_relative_url = [""];
      if (this.props.plane.className === jump_add) {
        tmp.create_object = [this.props.create_object_type];
      } else {
        if (this.props.plane.className === jump_unknown) {
          tmp.jump_unknown = [true];
        } else {
          tmp.relation_item_relative_url = this.props.jump_url;
        }
      }
      result[element.getAttribute('name')] = tmp;
      return result;
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        props = gadget.props,
        input = gadget.props.element.querySelector('input'),
        search_query,
        simple_query,
        field_json = props.field_json,
        ul = gadget.props.element.querySelector(".search_ul");

      function generateList(event) {
        var index = field_json.catalog_index,
          begin_from = props.begin_from || 0,
          lines = field_json.lines || 10,
          my_value = event.target.value;

        props.plane.className = jump_off;
        props.jump_url = [];
        ul.innerHTML = "";
        if (my_value === "") {
          props.spinner.className = searched;
          return;
        }
        simple_query = new SimpleQuery({
          key: index,
          value: my_value
        });
        props.spinner.className = searching;
        search_query =  Query.objectToSearchText(new ComplexQuery({
          operator: "AND",
          query_list: [gadget.props.query, simple_query]
        }));
        return new RSVP.Queue()
          .push(function () {
            return gadget.jio_allDocs({
              "query": search_query,
              "limit": [begin_from, begin_from + lines],
              "select_list": [index]
            });
          })
          .push(function (result) {
            var list = [],
              i,
              type = field_json.allow_creation ? field_json.portal_types : [],
              html;
            for (i = 0; i < result.data.rows.length; i += 1) {
              list.push({
                id: result.data.rows[i].id,
                value: result.data.rows[i].value[index]
              });
            }
            props.spinner.className = searched;
            html =  relation_listview_template({
              list: list,
              type: type,
              value: my_value
            });
            $(ul).toggle();
            ul.innerHTML = html;
            $(ul).toggle();
          });
      }


      function setSelectedElement(event) {
        var element = event.target,
          jump_url = element.getAttribute("data-relative-url"),
          create_object_type = element.getAttribute("data-create-object"),
          explore = element.getAttribute("data-explore");
        ul.innerHTML = "";

        if (jump_url) {
          props.input.value = element.textContent;
          props.jump_url = [jump_url];
          return gadget.getUrlFor({
            command: 'index',
            options: {
              jio_key: jump_url
            }
          }).push(function (url) {
            if (field_json.allow_jump) {
              props.plane.href = url;
              props.plane.className = jump_on;
            }
          });
        }
        if (create_object_type) {
          gadget.props.create_object_type = create_object_type;
          props.plane.className = jump_add;
          return;
        }
        if (explore) {
          return gadget.getFormContent({
            format: "json"
          })
            .push(function (content) {
              return gadget.redirect({
                command: 'index',
                options: {
                  page: "relation_search",
                  url: gadget.props.field_json.url,
                  extended_search: Query.objectToSearchText(simple_query),
                  view: gadget.props.field_json.view,
                  back_field: gadget.props.field_json.key,
                  target_index: gadget.props.index
                },
                form_content: content
              });
            });
        }
        props.plane.className = jump_unknown;
      }

      return RSVP.all([
        loopEventListener(input, 'input', false, generateList),
        loopEventListener(input, 'blur', false, function () {
          return new RSVP.Queue()
            .push(function () {
              return RSVP.any([
                RSVP.delay(200),
                promiseEventListener(ul, "click", true)
              ]);
            })
            .push(function (event) {
              var queue = new RSVP.Queue();
              if (event) {
                queue
                  .push(function () {
                    return setSelectedElement(event);
                  });
              }
              if (ul.innerHTML) {
                ul.innerHTML = "";
                props.plane.className = jump_unknown;
                if (gadget.props.addRelationInput) {
                  gadget.props.addRelationInput = false;
                  queue.push(function () {
                    return gadget.addRelationInput();
                  });
                }
              }
              return queue;
            });
        })]
        );
    })

    .declareService(function () {
      var gadget = this;

      function notifyInvalid(evt) {
        return gadget.notifyInvalid(evt.target.validationMessage);
      }

      // Listen to input change
      return loopEventListener(
        gadget.props.element.querySelector('input'),
        'invalid',
        false,
        notifyInvalid
      );
    })
    .declareService(function () {
      ////////////////////////////////////
      // Check field validity when the value changes
      ////////////////////////////////////
      var gadget = this;

      function notifyChange() {
        return gadget.notifyChange();
      }
      return loopEventListener(
        gadget.props.element.querySelector('input'),
        'change',
        false,
        notifyChange
      );
    });

}(window, rJS, RSVP, URI, loopEventListener, promiseEventListener,
  SimpleQuery, ComplexQuery, Query, QueryFactory, Handlebars, $));
