/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    notify_msg_template = Handlebars.compile(
      templater.getElementById("template-message-error").innerHTML
    );

  gadget_klass
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_remove", "jio_remove")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this,
        destroy_element = gadget.element.querySelector("#destroyOPML");
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i, value, len = result.data.total_rows;
          if (result.data.total_rows === 0) {
            destroy_element.setAttribute("disabled", "disabled");
          } else if (destroy_element.getAttribute("disabled") === "disabled") {
            destroy_element.setAttribute("disabled", "");
          }
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("active")) {
              result.data.rows[i].value.active = {
                field_gadget_param: {
                  css_class: "",
                  description: "Is Enabled",
                  hidden: 0,
                  "default": result.data.rows[i].value.active.toString(),
                  key: "active",
                  url: "gadget_erp5_field_status.html",
                  title: "Enabled",
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

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .onEvent('click', function (event) {
      var gadget = this,
        success = true,
        element = gadget.element.querySelector("#destroyOPML");

      function removeAllOPML(result) {
        var remove_queue = new RSVP.Queue(),
          i;

        function remove_opml(id) {
          remove_queue
            .push(function () {
              return gadget.jio_remove(id);
            });
        }

        for (i = 0; i < result.data.total_rows; i += 1) {
          remove_opml(result.data.rows[i].id);
        }
        return remove_queue;
      }

      if (element.getAttribute('rel') === 'destroying' &&
          event.target.id !== "destroyOPML") {
        element.setAttribute('rel', '');
        if (element.textContent.startsWith('[Confirm] ')) {
          element.textContent = element.textContent.slice(10, element.textContent.length);
        }
      }

      if (event.target.id === "destroyOPML") {
        if (element.getAttribute('rel') !== 'destroying') {
          element.setAttribute('rel', 'destroying');
          element.textContent = "[Confirm] " + element.textContent;
          return;
        }

        return gadget.notifySubmitting()
          .push(function () {
            element.setAttribute("disabled", "disabled");
            return gadget.jio_allDocs({
              query: 'portal_type: "opml"',
              select_list: ['title']
            })
              .push(function (result) {
                return RSVP.all([
                  removeAllOPML(result)
                ]);
              })
              .push(function () {
                return RSVP.all([
                  gadget.notifySubmitted({
                    message: 'All OPML removed',
                    status: 'success'
                  })
                ]);
              }, function () {
                success = false;
              });
          })
          .push(function () {
            element.textContent = element.textContent.slice(
              10,
              element.textContent.length
            );
            element.setAttribute('rel', '');
            if (success) {
              return gadget.redirect({"command": "reload"});
            }
          });
      }
    }, false, false)
    .onEvent('submit', function () {
      var gadget = this,
        doc;
      return gadget.notifySubmitting()
        .push(function () {
          return  gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (form_doc) {
          doc = form_doc;
          return gadget.setSetting('sync_check_offline',
            doc.check_online_access === "on" ? 'true' : 'false');
        })
        .push(function () {
          return gadget.setSetting('opml_add_auto_sync',
                                   doc.opml_add_auto_sync || "off");
        })
        .push(function () {
          return gadget.setSetting('sync_data_interval',
                                   parseInt(doc.auto_sync_interval, 10));
        })
        .push(function () {
          return gadget.setSetting('listbox_lines_limit',
                                   parseInt(doc.listbox_lines_limit, 10));
        })
        .push(function () {
          return gadget.setSetting('opml_import_limit',
                                   parseInt(doc.opml_import_limit, 10));
        })
        .push(function () {
          return RSVP.all([
            gadget.notifySubmitted({message: 'Parameters Updated', status: 'success'})
          ]);
        });
    })

    .declareMethod("triggerSubmit", function (event) {
      return this.element.querySelector('form button[type="submit"]').click();
    })

    .declareMethod("render", function (options) {
      if (options.url && options.username && options.password) {
        var redirect_options = {
            "url": options.url,
            "username": options.username,
            "password": options.password,
            "page": "ojsm_opml_add"
          };
        return this.redirect({"command": "display",
                              "options": redirect_options
                             });
      }
      var gadget = this,
        last_sync_time,
        sync_data_interval,
        check_online_access,
        listbox_lines_limit,
        opml_import_limit,
        opml_add_auto_sync;

      return new RSVP.Queue()
        .push(function () {
          return gadget.getSetting('opml_import_limit', 300);
        })
        .push(function (import_limit) {
          opml_import_limit = import_limit;
          return gadget.getSetting('listbox_lines_limit', 20);
        })
        .push(function (lines_limit) {
          listbox_lines_limit = lines_limit;
          return gadget.getSetting('sync_data_interval', 300000);
        })
        .push(function (sync_interval) {
          sync_data_interval = sync_interval;
          return gadget.getSetting('latest_sync_time', '');
        })
        .push(function (latest_sync_time) {
          last_sync_time = latest_sync_time;
          return gadget.getSetting("opml_add_auto_sync", "on");
        })
        .push(function (auto_sync) {
          opml_add_auto_sync = auto_sync;
          return gadget.getSetting("sync_check_offline", "true");
        })
        .push(function (sync_check_offline) {
          if (sync_check_offline === "true" || sync_check_offline === true ||
              sync_check_offline === undefined) {
            check_online_access = "on";
          } else {
            check_online_access = "";
          }
          return RSVP.all([
            gadget.getDeclaredGadget('form_view'),
            gadget.getSetting("portal_type")
          ]);
        })
        .push(function (result) {
          var column_list = [
            ['title', 'Title'],
            ['url', 'Url'],
            ['state', 'Requested State'],
            ['active', 'Sync Enabled']
          ];
          return result[0].render({
            erp5_document: {
              "_embedded": {"_view": {
                "your_last_sync_date": {
                  "description": "",
                  "title": "Last sync date",
                  "default": new Date(last_sync_time).toUTCString(),
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "last_sync_date",
                  "hidden": last_sync_time !== '' ? 0 : 1,
                  "timezone_style": 0,
                  "date_only": 0,
                  "type": "DateTimeField"
                },
                "my_auto_sync_interval": {
                  "description": "",
                  "title": "Auto Sync Time Interval",
                  "default": (sync_data_interval) + "",
                  "items": [["5 min", "300000"], ["10 min", "600000"],
                            ["15 min", "900000"], ["20 min", "1200000"],
                            ["30 min", "1800000"], ["1 h", "3600000"],
                            ["2 h", "7200000"]],
                  "editable": 1,
                  "key": "auto_sync_interval",
                  "hidden": 0,
                  "type": "ListField"
                },
                "my_listbox_lines_limit": {
                  "description": "Listbox Items lines per pages",
                  "title": "Listbox Items lines",
                  "default": (listbox_lines_limit) + "",
                  "items": [["20 lines per page", "20"], ["50 lines per page", "50"],
                            ["100 lines per page", "100"], ["200 lines per page", "200"],
                            ["500 lines per page", "500"]],
                  "editable": 1,
                  "key": "listbox_lines_limit",
                  "hidden": 0,
                  "type": "ListField"
                },
                "my_check_online_access": {
                  "description": "Check Online Access Before Sync",
                  "title": "Check Online Access",
                  "default": check_online_access,
                  "css_class": "",
                  "editable": 1,
                  "key": "check_online_access",
                  "hidden": 0,
                  "type": "CheckBoxField"
                },
                "my_opml_add_auto_sync": {
                  "description": "When Add OPML, start sync automatically",
                  "title": "Auto Sync Added OPML",
                  "default": opml_add_auto_sync,
                  "css_class": "",
                  "editable": 1,
                  "key": "opml_add_auto_sync",
                  "hidden": 0,
                  "type": "CheckBoxField"
                },
                "my_opml_import_limit": {
                  "description": "Maximum number of OPML to import",
                  "title": "OPML Import Limit",
                  "default": opml_import_limit,
                  "css_class": "",
                  "editable": 1,
                  "key": "opml_import_limit",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "listbox": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 1,
                  "editable_column_list": [],
                  "key": "monitoring_setting_listbox",
                  "lines": 20,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=portal_type%3A%22opml%22",
                  "portal_type": [],
                  "search_column_list": column_list,
                  "sort_column_list": column_list,
                  "sort": [['title', 'descending']],
                  "title": "OPML Documents",
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
                "left",
                [["your_last_sync_date"], ["my_auto_sync_interval"],
                 ["my_listbox_lines_limit"], ["my_opml_import_limit"],
                 ["my_check_online_access"], ["my_opml_add_auto_sync"]]
              ],
              [
                "right",
                []
              ],
              [
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: "change", options: {"page": "ojsm_opml_add"}}),
            gadget.getSetting('document_title')
          ]);
        })
        .push(function (result) {
          return gadget.updateHeader({
            page_title: result[1],
            save_action: true,
            add_url: result[0]
          });
        });
    });

}(window, rJS, RSVP, Handlebars));
