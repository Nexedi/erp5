/*global window, rJS, document, RSVP, escape */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, document, RSVP, escape) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .setState({
      ouline_list: "",
      instance_tree: ""
    })
    .ready(function (g) {
      g.props = {};
      g.props.parameter_form_list = [];
    })
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    //.declareAcquiredMethod("notifyError", 'notifyError')

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      param_list[0].select_list.push('_links');
      param_list[0].select_list.push('parameters');
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          return gadget.changeState({instance_dict: result});
        })
        .push(function () {
          var result = gadget.state.instance_dict,
            i,
            value,
            len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("date")) {
              result.data.rows[i].value.date = {
                field_gadget_param: {
                  allow_empty_time: 0,
                  ampm_time_style: 0,
                  css_class: "date_field",
                  date_only: 0,
                  description: "The Date",
                  editable: 0,
                  hidden: 0,
                  hidden_day_is_last_day: 0,
                  "default": result.data.rows[i].value.date,
                  key: "date",
                  required: 0,
                  timezone_style: 1,
                  title: "Status Date",
                  type: "DateTimeField"
                }
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
            if (result.data.rows[i].value.hasOwnProperty("status")) {
              value = result.data.rows[i].value.status;
              result.data.rows[i].value.status = {
                field_gadget_param: {
                  css_class: "",
                  description: "The Status",
                  hidden: 0,
                  "default": value,
                  key: "status",
                  url: "gadget_erp5_field_status.html",
                  title: "Status",
                  type: "GadgetField"
                }
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
          }
          return result;
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.updateHeader({
        title: 'Instance Trees View'
      })
        .push(function () {
          return gadget.jio_get(options.jio_key);
        })
        .push(function (hosting_doc) {
          return gadget.changeState({instance_tree: hosting_doc});
        })
        .push(function () {
          return gadget.jio_get(gadget.state.instance_tree.opml_url);
        })
        .push(function (opml_doc) {
          return gadget.changeState({opml: opml_doc});
        })
        .push(function () {
          return gadget.jio_allDocs({
            query: '(portal_type:"Opml Outline") AND (parent_id:"' +
              options.jio_key + '")'
          });
        })
        .push(function (ouline_list) {
          return gadget.changeState({ouline_list: ouline_list.data.rows});
        });
    })

    .onEvent('submit', function () {
      var gadget = this,
        i,
        promise_list = [];
      for (i = 0; i < gadget.props.parameter_form_list.length; i += 1) {
        promise_list.push(gadget.props.parameter_form_list[i].getLiveParameters());
      }
      return gadget.notifySubmitting()
        .push(function () {
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          var j,
            ok_to_save = true,
            return_list = [];
          for (j = 0; j < result_list.length; j += 1) {
            if (result_list[j].status !== 'OK') {
              ok_to_save = false;
              break;
            }
            return_list.push(gadget.props.parameter_form_list[j].saveContent());
          }
          if (ok_to_save) {
            return RSVP.all(return_list);
          }
          // One of storage failed, cancel save to be consistent
          return result_list;
        })
        .push(function (result_list) {
          var msg_list = [],
            j;
          for (j = 0; j < result_list.length; j += 1) {
            if (result_list[j].status !== "OK") {
              msg_list.push(result_list[j].stage + " from " + result_list[j].url);
            }
          }
          if (msg_list.length > 0) {
            return RSVP.all([
              gadget.notifySubmitted({
                message: 'Error while ' + msg_list.join('; '),
                status: 'error'
              })
            ]);
          }
          return RSVP.all([
            gadget.notifySubmitted({message: 'Parameters Updated', status: 'success'})
          ]);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      if (!modification_dict.hasOwnProperty('ouline_list') &&
          !modification_dict.hasOwnProperty('instance_dict')) {
        return;
      }
      if (modification_dict.hasOwnProperty('instance_dict')) {
        // render parameter form
        return new RSVP.Queue()
          .push(function () {
            var promise_list = [],
              i,
              element = gadget.element.querySelector('.parameters-box'),
              gadget_element;

            //cleanup
            while (element.hasChildNodes()) {
              element.removeChild(element.lastChild);
            }

            for (i = 0; i < gadget.state.instance_dict.data.total_rows; i += 1) {
              if (gadget.state.instance_dict.data.rows[i]
                  .value.aggregate_reference === undefined) {
                // Instance is not Synchronized!
                promise_list.push(false);
                continue;
              }
              gadget_element = document.createElement("div");
              element.appendChild(gadget_element);
              promise_list.push(
                gadget.declareGadget("gadget_officejs_monitoring_parameter_view.html",
                  {element: gadget_element,
                    scope: 'p_' + gadget.state.instance_dict.data.rows[i].id,
                    sandbox: "public"}
                  )
              );
            }
            return RSVP.all(promise_list);
          })
          .push(function (parameter_gadget_list) {
            var i,
              promise_list = [];
            gadget.props.parameter_form_list = parameter_gadget_list;
            for (i = 0; i < parameter_gadget_list.length; i += 1) {
              if (parameter_gadget_list[i]) {
                promise_list.push(
                  parameter_gadget_list[i].render({
                    url: gadget.state.instance_dict.data.rows[i].value._links.private_url.href
                      .replace('jio_private', 'private') + '/config',
                    basic_login: gadget.state.opml.basic_login,
                    title: "Parameters " + gadget.state.instance_dict.data.rows[i].value.title,
                    parameters: gadget.state.instance_dict.data.rows[i].value.parameters
                  })
                );
              }
            }
            return RSVP.all(promise_list);
          });
      }
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget('form_list');
        })
        .push(function (form_list) {
          var column_list = [
              ['title', 'Instance Title'],
              ['date', 'Status Date'],
              ['aggregate_reference', 'Computer'],
              ['status', 'Status']
            ],
            j,
            key_list = [],
            instance_query = '(portal_type:"Software Instance")';

          if (gadget.state.ouline_list.length === 0) {
            return;
          }
          for (j = 0; j < gadget.state.ouline_list.length; j += 1) {
            key_list.push('(parent_id:"' + gadget.state.ouline_list[j].id + '")');
          }
          instance_query += '(' + key_list.join('OR') + ')';
          return form_list.render({
            erp5_document: {
              "_embedded": {"_view": {
                "listbox": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 0,
                  "editable_column_list": [],
                  "key": "software_instance_listbox",
                  "lines": 20,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=" + escape(instance_query),
                  "portal_type": [],
                  "search_column_list": [],
                  "sort_column_list": column_list,
                  "sort": [["title", "ascending"]],
                  "title": "Software Instances",
                  "hide_sort": true,
                  "type": "ListBox"
                }
              }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'store_and_change', options: {
              page: "ojsm_jump",
              jio_key: gadget.state.instance_tree.opml_url,
              title: gadget.state.instance_tree.title,
              view_title: "Related OPML",
              search_page: "ojsm_status_list"
            }})
          ]);
        })
        .push(function (url_list) {
          if (gadget.state.instance_tree.instance_amount === 0) {
            gadget.element.querySelector('.hosting-title').textContent =
              gadget.state.instance_tree.title + " -  Not synchronized!";
            return gadget.updateHeader({
              page_title: "Instance Tree: " + gadget.state.instance_tree.title,
              selection_url: url_list[0],
              jump_url: url_list[1]
            });
          }
          gadget.element.querySelector('.hosting-title').textContent =
            gadget.state.instance_tree.title;
          return gadget.updateHeader({
            page_title: "Instance Tree: " + gadget.state.instance_tree.title,
            selection_url: url_list[0],
            jump_url: url_list[1],
            save_action: true
          });
        });
    });

}(window, rJS, document, RSVP, escape));