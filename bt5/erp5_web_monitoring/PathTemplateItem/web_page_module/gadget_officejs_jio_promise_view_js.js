/*global window, rJS, RSVP, Handlebars, RegExp, document, atob */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars, RegExp, document, atob) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
      .querySelector(".render-link-template")
      .innerHTML,
    link_template = Handlebars.compile(source);

  function getPromiseTextContent(content, private_url) {
    /*jslint regexp: true*/
    var regex = /(https?:\/\/[^\s]+)/g,
      i,
      parser,
      private_parser = document.createElement('a'),
      result_list = content.match(regex),
      url_list = [];
    /*jslint regexp: false*/

    function makeUnique(array_list) {
      var temp = {},
        l,
        r = [],
        k;
      for (l = 0; l < array_list.length; l += 1) {
        temp[array_list[l]] = true;
      }
      for (k in temp) {
        if (temp.hasOwnProperty(k)) {
          r.push(k);
        }
      }
      return r;
    }

    private_parser.href = private_url;
    if (result_list !== null && result_list !== undefined) {
      result_list = makeUnique(result_list);
      for (i = 0; i < result_list.length; i += 1) {
        parser = document.createElement('a');
        parser.href = result_list[i];
        parser.target = 'blank';
        parser.textContent = result_list[i];
        if (parser.hostname === private_parser.hostname) {
          // set the password
          parser.username = private_parser.username;
          parser.password = private_parser.password;
        }
        url_list.push({
          url: result_list[i],
          next: parser.outerHTML
        });
      }
    }

    content = content.replace(/\n/g, '<br/>');
    for (i = 0; i < url_list.length; i += 1) {
      content = content.replace(
        new RegExp(url_list[i].url, 'g'),
        url_list[i].next
      );
    }
    return content;
  }

  gadget_klass
    .setState({
      jio_gadget: ""
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
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("redirect", "redirect")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        software_instance,
        opml_doc;

      return new RSVP.Queue()
        .push(function () {
          return gadget.state.jio_gadget.createJio({
            type: "webhttp",
            // XXX fix of url
            url: options.doc.source_url.replace("jio_public", "public")
          });
        })
        .push(function () {
          return gadget.jio_allDocs({
            select_list: [
              "parent_url",
              "parent_id",
              "title",
              "opml_title",
              "portal_type",
              "_links",
              "_embedded",
              "reference",
              "aggregate_reference",
              "ipv6",
              "ipv4",
              "partition_id",
              "software_release"
            ],
            query: '(portal_type:"Software Instance") AND (parent_id:"' +
              options.doc.parent_id + '")'
          });
        })
        .push(function (result) {
          var i;
          for (i = 0; i < result.data.total_rows; i += 1) {
            software_instance = result.data.rows[i].value;
          }
          // get opml outline
          return gadget.jio_get(options.doc.parent_id);
        })
        .push(function (outline_doc) {
          // get opml
          return RSVP.all([outline_doc.parent_id,
                           gadget.jio_get(outline_doc.parent_url)]);
        })
        .push(function (document_list) {
          opml_doc = document_list[1];
          return gadget.getUrlFor({command: 'push_history', options: {
            jio_key: document_list[0]
          }});
        })
        .push(function (hosting_url) {
          var pass_url;

          if (software_instance === undefined) {
            // synchronisation problem, probably invalid password
            software_instance = {_links: {private_url: {href: ""},
                                          public_url: {href: ""}},
                                 _embedded: {instance: {}}};
          }
          if (software_instance._embedded !== undefined &&
              software_instance._embedded.hasOwnProperty('instance')) {
            software_instance.ipv6 = software_instance._embedded.instance.ipv6;
            software_instance.ipv4 = software_instance._embedded.instance.ipv4;
            software_instance.partition_id = software_instance._embedded.instance.partition;
            software_instance.software_release = software_instance._embedded.instance['software-release'];
          }
          // fix URLs
          software_instance._links.private_url.href = software_instance
            ._links.private_url.href.replace("jio_private", "private");
          software_instance._links.public_url.href = software_instance
            ._links.public_url.href.replace("jio_public", "public");

          pass_url = "https://" + atob(opml_doc.basic_login) +
            "@" + software_instance._links.private_url.href.split("//")[1];

          return gadget.changeState({
            promise: options.doc,
            jio_key: options.jio_key,
            status: options.doc.category,
            status_date: new Date(options.doc.pubDate),
            report_date: new Date(options.doc.lastBuildDate),
            title: options.doc.source,
            promise_output: options.doc.description,
            private_url: pass_url,
            public_url: software_instance._links.public_url.href,
            instance_reference: software_instance.reference,
            instance_title: software_instance.title,
            hosting_title: opml_doc.title,
            hosting_url: hosting_url,
            partition_ipv6: software_instance.ipv6,
            partition_ipv4: software_instance.ipv4,
            computer_partition: software_instance.partition_id,
            computer_reference: software_instance.aggregate_reference,
            software_release: software_instance.software_release
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
      var gadget = this,
        result = {};
      if (param_list[0].query.indexOf('portal_type:"promise"') !== -1) {
        // get history file on live
        result.data = {rows: [], total_rows: 0};
        return gadget.state.jio_gadget.get(
          gadget.state.promise.source + ".history"
        )
          .push(undefined, function (error) {
            if (error.name === "cancel") {
              return undefined;
            }
            return gadget.notifySubmitted({
              status: "error",
              message: "Failed to get promise history content! \n" +
                error.message || ''
            })
              .push(function () {
                return undefined;
              });
          })
          .push(function (status_history) {
            var i,
              len,
              start;

            if (status_history && status_history.hasOwnProperty('data')) {
              // the status history list is reversed ([old, ...., newest])
              len = status_history.data.length;
              start = len - param_list[0].limit[0] - 1;
              //lines = param_list[0].limit[1] - param_list[0].limit[0];
              if (start < 0) {
                start = len - 1;
              }
              //if (lines > len) {
              //  lines = len - start;
              //}
              for (i = start; i >= 0; i -= 1) {
                result.data.total_rows += 1;
                result.data.rows.push({
                  value: {
                    status: {
                      field_gadget_param: {
                        css_class: "",
                        description: "The Status",
                        hidden: 0,
                        "default": status_history.data[i].status,
                        key: "status",
                        url: "gadget_erp5_field_status.html",
                        title: "Status",
                        type: "GadgetField"
                      }
                    },
                    start_date: {
                      field_gadget_param: {
                        allow_empty_time: 0,
                        ampm_time_style: 0,
                        css_class: "date_field",
                        date_only: 0,
                        description: "The Date",
                        editable: 0,
                        hidden: 0,
                        hidden_day_is_last_day: 0,
                        "default": new Date(
                          status_history.data[i].date ||
                            status_history.data[i]['start-date']
                        ).toUTCString(),
                        key: "start_date",
                        required: 0,
                        timezone_style: 0,
                        title: "Date",
                        type: "DateTimeField"
                      }
                    },
                    change_date:  {
                      field_gadget_param: {
                        allow_empty_time: 0,
                        ampm_time_style: 0,
                        css_class: "date_field",
                        date_only: 0,
                        description: "The Date",
                        editable: 0,
                        hidden: 0,
                        hidden_day_is_last_day: 0,
                        "default": new Date(
                          status_history.data[i]['change-date'] ||
                            status_history.data[i]['change-time'] * 1000
                        ).toUTCString(),
                        key: "change_date",
                        required: 0,
                        timezone_style: 0,
                        title: "Status Date",
                        type: "DateTimeField"
                      }
                    },
                    message: status_history.data[i].message,
                    "listbox_uid:list": {
                      key: "listbox_uid:list",
                      value: 2713
                    }
                  }
                });
              }
            }
            return result;
          });
      }
    })
    .onStateChange(function () {
      var gadget = this;
      if (!gadget.state.hasOwnProperty('status') &&
          !gadget.state.hasOwnProperty('title')) {
        return;
      }
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          var column_list = [
              ['status', 'Status'],
              ['start_date', 'Report Date'],
              ['change_date', 'Status Date'],
              ['message', 'Promise Output']
            ];
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "your_title": {
                  "description": "",
                  "title": "Promise Title",
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
                "your_status_date": {
                  "description": "",
                  "title": "Status Since",
                  "default": gadget.state.status_date.toUTCString(),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "status_date",
                  "hidden": 0,
                  "timezone_style": 0,
                  "date_only": 0,
                  "type": "DateTimeField"
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
                "your_software_release_url": {
                  "description": "",
                  "title": "Software Release",
                  "default": link_template({
                    url: gadget.state.software_release,
                    title: "Access Software release",
                    target: "_blank"
                  }),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "software_release_url",
                  "hidden": 0,
                  "type": "EditorField"
                },
                "your_promise_output": {
                  "description": "",
                  "title": "Promise Output Message",
                  "default": getPromiseTextContent(gadget.state.promise_output,
                    gadget.state.private_url),
                  "css_class": "promise-output",
                  "required": 0,
                  "editable": 0,
                  "key": "promise_output",
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
                "your_instance_title": {
                  "description": "",
                  "title": "Software Instance",
                  "default": [gadget.state.instance_title],
                  "query": "urn:jio:allDocs?query=%28portal_type%3A%22" +
                    "Opml Outline" + "%22%29AND%28reference%3A%22" +
                    gadget.state.instance_reference + "%22%29",
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "instance_title",
                  "hidden": gadget.state.instance_reference ? 0 : 1,
                  "view": "view",
                  "allow_jump": true,
                  "allow_creation": false,
                  "sort": [],
                  "relation_item_relative_url": [gadget.state.instance_reference],
                  "type": "RelationStringField"
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
                "your_promise_history": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 0,
                  "editable_column_list": [],
                  "key": "promise_history",
                  "lines": 60,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=portal_type%3A%22" +
                    "promise" + "%22",
                  "portal_type": [],
                  "search_column_list": [],
                  "sort_column_list": [],
                  "sort": [],
                  "hide_sort": true,
                  "command": "reload",
                  "title": "Promise Status list (On live)",
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
              group_list: [
                [
                  "left",
                  [
                    ["your_title"], ["your_status"], ["your_status_date"],
                    ["your_report_date"], ["your_public_url"], ["your_private_url"]
                  ]
                ],
                [
                  "right",
                  [
                    ["your_hosting_title"], ["your_instance_title"],
                    ["your_computer_reference"], ["your_computer_partition"],
                    ["your_partition_ipv6"], ["your_software_release_url"]
                  ]
                ],
                [
                  "center",
                  [["your_promise_output"]]
                ],
                [
                  "bottom",
                  [["your_promise_history"]]
                ]
              ]
            }
          });
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
            page_title: "Promise: " + gadget.state.title,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2],
            refresh_action: true
          });
        });
    });
}(window, rJS, RSVP, Handlebars, RegExp, document, atob));
