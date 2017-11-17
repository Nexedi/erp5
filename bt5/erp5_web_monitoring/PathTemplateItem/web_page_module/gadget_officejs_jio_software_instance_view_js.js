/*global window, rJS, RSVP, Handlebars, atob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, atob) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
      .querySelector(".render-link-template")
      .innerHTML,
    link_template = Handlebars.compile(source);
  gadget_klass
    .setState({
      jio_gadget: "",
      instance: "",
      opml: "",
      opml_outline: "",
      graph_value: {}
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_gadget")
        .push(function (jio_gadget) {
          return gadget.changeState({"jio_gadget": jio_gadget});
        });
    })
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.changeState({instance: options.doc});
        })
        .push(function () {
          // Get opml outline document
          return gadget.jio_get(gadget.state.instance.parent_id);
        })
        .push(function (opml_outline) {
          return gadget.changeState({
            opml_outline: opml_outline
          });
        })
        .push(function () {
          return gadget.jio_get(gadget.state.opml_outline.parent_url);
        })
        .push(function (opml_doc) {
          return gadget.changeState({
            opml: opml_doc
          });
        })
        .push(function () {
          return gadget.state.jio_gadget.createJio({
            type: "webhttp",
            // XXX fix of url
            url: gadget.state.instance._links.private_url.href
              .replace("jio_private", "private") +
              'documents/',
            basic_login: gadget.state.opml.basic_login
          });
        })
        .push(function () {
          return gadget.getUrlFor({command: 'push_history', options: {
            jio_key: options.doc.reference,
            page: 'ojsm_hosting_subscription_view',
            opml_key: gadget.state.opml.url
          }});
        })
        .push(function (hosting_url) {
          var pass_url,
            public_url,
            private_url,
            current_document = gadget.state.instance;

          // fix URLs
          private_url = gadget.state.instance._links
            .private_url.href.replace("jio_private", "private");
          public_url = gadget.state.instance._links
            .public_url.href.replace("jio_public", "public");
          pass_url = "https://" + atob(gadget.state.opml.basic_login) +
            "@" + private_url.split("//")[1];

          return gadget.changeState({
            jio_key: options.jio_key,
            status: gadget.state.instance.status,
            report_date: new Date(gadget.state.instance.date),
            title: current_document.title,
            error: current_document.state.error,
            success: current_document.state.success,
            public_url: public_url,
            private_url: pass_url,
            rss_url: current_document._links.rss_url.href,
            //resource_url: tmp_url,
            //process_url: tmp_process_url,
            hosting_title: gadget.state.opml.title,
            hosting_url: hosting_url,
            partition_ipv6: current_document._embedded.instance.ipv6,
            partition_ipv4: current_document._embedded.instance.ipv4,
            computer_partition: current_document._embedded.instance.partition,
            computer_reference: current_document._embedded.instance.computer,
            software_release: current_document._embedded.instance['software-release']
          });
        });
    })

    .onEvent('submit', function () {
      // ON submit, refresh page
      return this.redirect({command: 'reload'});
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i, value, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("lastBuildDate")) {
              value = new Date(result.data.rows[i].value.lastBuildDate);
              result.data.rows[i].value.lastBuildDate = {
                allow_empty_time: 0,
                ampm_time_style: 0,
                css_class: "date_field",
                date_only: 0,
                description: "The Date",
                editable: 0,
                hidden: 0,
                hidden_day_is_last_day: 0,
                "default": value.toUTCString(),
                key: "lastBuildDate",
                required: 0,
                timezone_style: 0,
                title: "Promise Date",
                type: "DateTimeField"
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
            if (result.data.rows[i].value.hasOwnProperty("comments")) {
              value = result.data.rows[i].value.comments.slice(0, 30);
              if (result.data.rows[i].value.comments.length >= 30) {
                value += "...";
              }
              result.data.rows[i].value.comments = {
                css_class: "string_field",
                description: "The Message",
                editable: 0,
                hidden: 0,
                "default": value,
                key: "comments",
                required: 0,
                title: "Message",
                type: "StringField"
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
            if (result.data.rows[i].value.hasOwnProperty("category")) {
              value = result.data.rows[i].value.category;
              result.data.rows[i].value.category = {
                css_class: "",
                description: "The Status",
                hidden: 0,
                "default": value,
                key: "category",
                url: "gadget_erp5_field_status.html",
                title: "Status",
                type: "GadgetField"
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
    .onStateChange(function () {
      var gadget = this,
        graph_value = {};
      if (!gadget.state.hasOwnProperty('status') &&
          !gadget.state.hasOwnProperty('title')) {
        return;
      }
      return new RSVP.Queue()
        .push(function () {
          // Move this to not slow down the page rendering...
          return gadget.state.jio_gadget.get(
            gadget.state.instance.data.state
          )
            .push(undefined, function (error) {
              return gadget.notifySubmitted({
                message: "Warning: Failed to download monitoring state history file!\n " +
                  error.message || "",
                status: "error"
              })
                .push(function () {
                  return {};
                });
            })
            .push(function (element_dict) {
              var promise_data = [
                  "Date, Success, Error, Warning",
                  new Date() + ",0,0,0"
                ],
                data = element_dict.data || promise_data,
                data_list = [],
                line_list,
                i;

              data_list.push({
                value_dict: {"0": [], "1": []},
                type: "scatter",
                axis_mapping_id_dict: {"1": "1_1"},
                title: "promises success"
              });
              data_list.push({
                value_dict: {"0": [], "1": []},
                type: "scatter",
                axis_mapping_id_dict: {"1": "1_2"},
                title: "promises error"
              });
              for (i = 1; i < data.length; i += 1) {
                line_list = data[i].split(',');
                data_list[0].value_dict["0"].push(line_list[0]);
                data_list[0].value_dict["1"].push(line_list[1]);

                // XXX repeating date entry
                data_list[1].value_dict["0"].push(line_list[0]);
                data_list[1].value_dict["1"].push(line_list[2]);
              }
              graph_value = {
                data: data_list,
                layout: {
                  axis_dict : {
                    "0": {
                      "title": "Success/Failure Progression",
                      "scale_type": "linear",
                      "value_type": "date"
                    },
                    "1_1": {
                      "title": "Promises success",
                      "position": "right"
                    },
                    "1_2": {
                      "title": "Promises error",
                      "position": "right"
                    }
                  },
                  title: "Success/Failure Progression"
                }
              };
            });
        })
        .push(function () {
          //gadget.element.querySelector('.template-view').innerHTML = html;
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          var column_list = [
            ['source', 'Promise'],
            ['lastBuildDate', 'Promise Date'],
            ['comments', 'Message'],
            ['category', 'Status']
          ];
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "your_title": {
                  "description": "",
                  "title": "Instance Title",
                  "default": gadget.state.title,
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "title",
                  "hidden": 0,
                  "type": "StringField"
                },
                "your_status": {
                  "description": "",
                  "title": "Status",
                  "default": gadget.state.status,
                  "css_class": "",
                  "required": 1,
                  "editable": 0,
                  "key": "status",
                  "hidden": 0,
                  "url": "gadget_erp5_field_status.html",
                  "type": "GadgetField"
                },
                "your_report_date": {
                  "description": "",
                  "title": "Report Date",
                  "default": gadget.state.report_date.toUTCString(),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "report_date",
                  "hidden": 0,
                  "timezone_style": 0,
                  "date_only": 0,
                  "type": "DateTimeField"
                },
                "your_public_url": {
                  "description": "",
                  "title": "Public Logs Url",
                  "default": link_template({
                    url: gadget.state.public_url,
                    title: "Access Public files",
                    target: "_blank"
                  }),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "public_url",
                  "hidden": 0,
                  "type": "EditorField"
                },
                "your_private_url": {
                  "description": "",
                  "title": "Private Logs Url",
                  "default": link_template({
                    url: gadget.state.private_url,
                    title: "Access Private files",
                    target: "_blank"
                  }),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "private_url",
                  "hidden": 0,
                  "type": "EditorField"
                },
                "your_error_count": {
                  "description": "",
                  "title": "Promises Error",
                  "default": String(gadget.state.error),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "error_count",
                  "hidden": 0,
                  "type": "StringField"
                },
                "your_success_count": {
                  "description": "",
                  "title": "Promises OK",
                  "default": String(gadget.state.success),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "success_count",
                  "hidden": 0,
                  "type": "StringField"
                },
                "your_software_release_url": {
                  "description": "",
                  "title": "Software Release",
                  "default": link_template({
                    url: gadget.state.software_release,
                    title: "Access link",
                    target: "_blank"
                  }),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "software_release_url",
                  "hidden": 0,
                  "type": "EditorField"
                },
                "your_rss_url": {
                  "description": "",
                  "title": "RSS Link",
                  "default": link_template({
                    url: gadget.state.rss_url,
                    title: "Access RSS",
                    target: "_blank"
                  }),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "rss_url",
                  "hidden": 0,
                  "type": "EditorField"
                },
                "your_hosting_title": {
                  "description": "",
                  "title": "Hosting Subscription",
                  "default": link_template({
                    url: gadget.state.hosting_url,
                    title: gadget.state.hosting_title
                  }),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "hosting_title",
                  "hidden": 0,
                  "type": "EditorField"
                },
                "your_computer_reference": {
                  "description": "",
                  "title": "Computer",
                  "default": gadget.state.computer_reference,
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "computer_reference",
                  "hidden": 0,
                  "type": "StringField"
                },
                "your_computer_partition": {
                  "description": "",
                  "title": "Partition",
                  "default": gadget.state.computer_partition,
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "computer_partition",
                  "hidden": 0,
                  "type": "StringField"
                },
                "your_partition_ipv6": {
                  "description": "",
                  "title": "Partition IPv6",
                  "default": gadget.state.partition_ipv6,
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "partition_ipv6",
                  "hidden": 0,
                  "type": "StringField"
                },
                "your_partition_ipv4": {
                  "description": "",
                  "title": "Partition IPv4",
                  "default": gadget.state.partition_ipv4,
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "partition_ipv4",
                  "hidden": 0,
                  "type": "StringField"
                },
                "your_instance_promise_list": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 0,
                  "editable_column_list": [],
                  "key": "instance_promise_list",
                  "lines": 60,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=%28portal_type%3A%22" +
                    "promise" + "%22%29AND%28parent_id%3A%22" +
                    gadget.state.instance.parent_id + "%22%29",
                  "portal_type": [],
                  "search_column_list": column_list,
                  "sort_column_list": column_list,
                  "sort": [["category", "ascending"]],
                  "hide_sort": true,
                  "title": "Instance Promises Status",
                  "type": "ListBox"
                },
                "your_graph_status": {
                  css_class: "no_label",
                  description: "The Graph Status",
                  hidden: 0,
                  "default": graph_value || {},
                  key: "graph_status",
                  url: "gadget_field_graph_dygraph.html",
                  title: "",
                  type: "GadgetField"
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
              group_list: [
                [
                  "left",
                  [
                    ["your_title"], ["your_status"], ["your_status_date"],
                    ["your_report_date"], ["your_error_count"],
                    ["your_success_count"], ["your_public_url"],
                    ["your_private_url"]
                  ]
                ],
                [
                  "right",
                  [
                    ["your_hosting_title"], ["your_instance_title"],
                    ["your_computer_reference"], ["your_computer_partition"],
                    ["your_partition_ipv4"], ["your_partition_ipv6"],
                    ["your_software_release_url"], ["your_rss_url"]
                  ]
                ],
                [
                  "center",
                  [["your_graph_status"]]
                ],
                [
                  "bottom",
                  [["your_instance_promise_list"]]
                ]
              ]
            }
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.getUrlFor({command: 'push_history', options: {
              page: 'ojsm_resources_view',
              key: gadget.state.opml_outline.reference
            }}),
            gadget.getUrlFor({command: 'push_history', options: {
              page: 'ojsm_processes_view',
              key: gadget.state.opml_outline.reference
            }})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Instance: " + gadget.state.title,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2],
            resources_url: url_list[3],
            processes_url: url_list[4],
            refresh_action: true
          });
        });
    });
}(window, rJS, RSVP, Handlebars, atob));
