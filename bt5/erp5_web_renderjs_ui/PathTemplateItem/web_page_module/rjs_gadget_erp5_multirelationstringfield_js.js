/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, URI, loopEventListener, Handlebars, Event, document,
 SimpleQuery, ComplexQuery, Query, QueryFactory, promiseEventListener, $*/
(function (window, rJS, RSVP, URI, loopEventListener, promiseEventListener, document,
  SimpleQuery, ComplexQuery, Query, QueryFactory, Handlebars, Event, $) {
  "use strict";


  var gadget_klass = rJS(window),
    single_input_source = gadget_klass.__template_element
                         .getElementById("single-input-template")
                         .innerHTML,
    single_input_template = Handlebars.compile(single_input_source),

    relation_listview_source = gadget_klass.__template_element
                         .getElementById("relation-listview-template")
                         .innerHTML,
    relation_listview_template = Handlebars.compile(relation_listview_source),
    multi_input_source = gadget_klass.__template_element
                         .getElementById("multi-input-template")
                         .innerHTML,
    multi_input_template = Handlebars.compile(multi_input_source),
    create_source = gadget_klass.__template_element
                         .getElementById("create-template")
                         .innerHTML,
    create_template = Handlebars.compile(create_source),

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




  function listenToInput(gadget, index) {
    var props = gadget.props,
      div = gadget.props.element.querySelectorAll('.single_input')[index],
      input = div.querySelector('input'),
      search_query,
      simple_query,
      plane = div.querySelector('.ui-btn'),
      field_json = props.field_json,
      spinner = div.querySelector('.ui-hidden-accessible'),
      create_div = div.querySelector(".ui-tag-list"),
      ul = div.querySelector(".search_ul");

    function generateList(event) {
      var catalog_index = field_json.catalog_index,
        begin_from = props.begin_from || 0,
        lines = field_json.lines || 10,
        my_value = event.target.value;

      ul.innerHTML = "";
      create_div.innerHTML = "";
      plane.className = jump_off;
      props.jump_url[index] = "";
      if (my_value === "") {
        spinner.className = searched;
        return;
      }
      simple_query = new SimpleQuery({
        key: catalog_index,
        value: my_value
      });
      spinner.className = searching;
      search_query =  Query.objectToSearchText(new ComplexQuery({
        operator: "AND",
        query_list: [gadget.props.query, simple_query]
      }));
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs({
            "query": search_query,
            "limit": [begin_from, begin_from + lines],
            "select_list": [catalog_index]
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
              value: result.data.rows[i].value[catalog_index]
            });
          }
          spinner.className = searched;
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
        explore = element.getAttribute("data-explore"),
        tmp;
      ul.innerHTML = "";

      if (index === gadget.props.last_index - 1 && !explore) {
        props.jump_url[gadget.props.last_index] = "";
        tmp = document.createElement("fieldset");
        tmp.innerHTML = single_input_template();
        gadget.props.container.appendChild(tmp);
        gadget.props.input_list.push({
          "title": field_json.key,
          "name": field_json.key,
          "value": "",
          "href": "",
          "create_object": ""
        });
        gadget.props.last_index += 1;
        gadget.props.element.dispatchEvent(new Event('add_relation_input'));
      }
      if (jump_url) {
        props.jump_url[index] = jump_url;
        input.value = element.textContent;
        return gadget.getUrlFor({
          command: 'index',
          options: {
            jio_key: jump_url
          }
        }).push(function (url) {
          if (field_json.allow_jump) {
            plane.href = url;
            plane.className = jump_on;
          }
        });
      }
      if (create_object_type) {
        input.setAttribute("data-create-object", create_object_type);
        plane.className = jump_add;
        create_div.innerHTML = create_template({'text': create_object_type});
        return;
      }

      if (explore) {
        return new RSVP.Queue()
          .push(function () {
            return gadget.getNonSavedPageContent();
          })
          .push(function (stored_data) {
            return gadget.relation_jump({
              command: 'index',
              options: {
                page: "relation_search",
                url: gadget.props.field_json.url,
                extended_search: Query.objectToSearchText(simple_query),
                view: gadget.props.field_json.view,
                back_field: gadget.props.field_json.key,
                target_index: index,
                stored_data: stored_data
              }
            });
          });
      }
      plane.className = jump_unknown;
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
            var tmp;
            if (event) {
              return setSelectedElement(event);
            }
            if (ul.innerHTML) {
              ul.innerHTML = "";
              plane.className = jump_unknown;
              if (index === gadget.props.last_index - 1) {
                props.jump_url[gadget.props.last_index] = "";
                tmp = document.createElement("fieldset");
                tmp.innerHTML = single_input_template();
                gadget.props.container.appendChild(tmp);
                gadget.props.input_list.push({
                  "title": field_json.key,
                  "name": field_json.key,
                  "value": "",
                  "href": "",
                  "create_object": ""
                });
                gadget.props.last_index += 1;
                gadget.props.element.dispatchEvent(new Event('add_relation_input'));
              }
            }
          });
      })]
      );
  }


  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("relation_jump", "relation_jump")
    .declareAcquiredMethod("getNonSavedPageContent", "getNonSavedPageContent")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this,
        i,
        field_json = options.field_json || {},
        target_url_list = [],
        list = [],
        input = [],
        value_list = field_json.default || [];
      if (field_json.relation_item_relative_url) {
        target_url_list = field_json.relation_item_relative_url;
      }
      gadget.props.field_json = field_json;
      gadget.props.jump_url = [];
      field_json.create_object = field_json.create_object || [];
      field_json.jump_unknown = field_json.jump_unknown || [];
      gadget.props.query = QueryFactory.create(new URI(field_json.query).query(true).query);
      return new RSVP.Queue()
        .push(function () {
          for (i = 0; i < value_list.length; i += 1) {
            if (!value_list[i]) {
              if (field_json.uid) {
                return gadget.jio_allDocs({
                  query:  Query.objectToSearchText(new SimpleQuery({
                    key: "catalog.uid",
                    value: field_json.uid
                  })),
                  limit: [0, 1],
                  select_list: [field_json.catalog_index]
                });
              }
            }
          }
        })
        .push(function (result) {
          var non_empty_input = true;
          list = [];
          if (result) {
            value_list[i] = result.data.rows[0].value[field_json.catalog_index];
          }
          for (i = 0; i < target_url_list.length; i += 1) {
            if (target_url_list[i]) {
              gadget.props.jump_url.push(target_url_list[i]);
              list.push(gadget.getUrlFor({
                command: 'index',
                options: {
                  jio_key: target_url_list[i]
                }
              }));
            } else {
              if (!field_json.create_object[i]) {
                //non jump url nor create onject
                non_empty_input = false;
              }
              gadget.props.jump_url.push("");
              list.push("");
            }
          }
          if (non_empty_input) {
            value_list.push("");
            list.push("");
            gadget.props.jump_url.push("");
          }
          return RSVP.all(list);
        })
        .push(function (href_list) {
          for (i = 0; i < value_list.length; i += 1) {
            input.push({
              "create_object": field_json.create_object[i],
              "title": field_json.key,
              "name": field_json.key,
              "value": value_list[i],
              "href": href_list[i],
              "jump_unknown": field_json.jump_unknown[i],
              "error_text": field_json.error_text
            });
          }
          gadget.props.input_list = input;
          gadget.props.default_index = input.length;
          gadget.props.last_index = input.length;
          return gadget.translateHtml(multi_input_template({
            input: input,
            allow_jump: field_json.allow_jump,
            readonly: field_json.editable ? "" : "ui-state-readonly"
          }));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          gadget.props.container = gadget.props.element.querySelector(".container");
        });
    })
    .declareMethod('getContent', function () {
      var list = this.props.element.querySelectorAll('.single_input'),
        result = {},
        i,
        input,
        value_list = [],
        plane,
        field_json = this.props.field_json;
      for (i = 0; i < list.length - 1; i += 1) {
        plane = list[i].querySelector('.ui-btn');
        input = list[i].querySelector('input');
        if (plane.className === jump_add) {
          result[field_json.relation_field_id + "_" + i] = "_newContent_" + input.getAttribute("data-create-object");
        }
        value_list.push(input.value);
      }
      result[field_json.key] = value_list;
      return result;
    })
    .declareMethod('getNonSavedValue', function () {
      var list = this.props.element.querySelectorAll('.single_input'),
        result = {},
        i,
        input,
        plane,
        field_json = this.props.field_json;
      field_json.create_object = [];
      field_json.jump_known = [];
      delete field_json.uid;
      for (i = 0; i < list.length; i += 1) {
        plane = list[i].querySelector('.ui-btn');
        input = list[i].querySelector('input');
        field_json.default[i] = input.value;
        field_json.jump_unknown[i] = "";
        field_json.create_object[i] = "";
        if (plane.className === jump_add) {
          field_json.create_object[i] = input.getAttribute("data-create-object");
        } else {
          if (plane.className === jump_unknown) {
            field_json.jump_unknown[i] = true;
          }
        }
      }
      field_json.relation_item_relative_url = this.props.jump_url;
      result[field_json.key] = field_json;
      return result;
    })
    .declareService(function () {
      var i,
        gadget = this,
        list = [];

      for (i = 0; i < gadget.props.last_index; i += 1) {
        list.push(listenToInput(gadget, i));
      }
      return RSVP.all(list);
    })
    .declareService(function () {
      var gadget = this;
      return loopEventListener(gadget.props.element, 'add_relation_input', false, function () {
        var list = [],
          i;
        for (i = gadget.props.default_index; i < gadget.props.last_index; i += 1) {
          list.push(listenToInput(gadget, i));
        }
        return RSVP.all(list);
      });
    });
}(window, rJS, RSVP, URI, loopEventListener, promiseEventListener, document,
  SimpleQuery, ComplexQuery, Query, QueryFactory, Handlebars, Event, $));
