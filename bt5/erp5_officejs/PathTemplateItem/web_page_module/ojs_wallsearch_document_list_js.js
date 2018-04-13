/*global window, rJS, RSVP, console */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlForAcquired", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      param_list[0].select_list.push('story');
      param_list[0].select_list.push('link');
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i, date, message, link, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("created_time")) {
              date = new Date(result.data.rows[i].value.created_time);
              result.data.rows[i].value.created_time = {
                field_gadget_param: {
                  allow_empty_time: 0,
                  ampm_time_style: 0,
                  css_class: "date_field",
                  date_only: 0,
                  description: "The Date",
                  editable: 0,
                  hidden: 0,
                  hidden_day_is_last_day: 0,
                  "default": date.toUTCString(),
                  key: "modification_date",
                  required: 0,
                  timezone_style: 0,
                  title: "Modification Date",
                  type: "DateTimeField"
                }
              };
              result.data.rows[i].value["listbox_uid:list"] = {
                key: "listbox_uid:list",
                value: 2713
              };
            }
            if (!result.data.rows[i].value.message) {
              message = '';
            } else {
              message = result.data.rows[i].value.message;
            }
            if (result.data.rows[i].value.story) {
              message += ' ' + result.data.rows[i].value.story;
            }
            link = result.data.rows[i].value.link;
            if (link) {
              if (message.indexOf(link.slice(0, -1)) === -1) {
                message += ' ' + result.data.rows[i].value.link.slice(0, 100) + '...';
              }
            }
            result.data.rows[i].value.message = message;
          }
          return result;
        });
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })

    .allowPublicAcquisition("getUrlFor", function (param_list) {
      var gadget = this;
      if (param_list[0].command === 'index') {
        return gadget.jio_get(param_list[0].options.jio_key)
          .push(function (result) {
            if (result.link) {
              return result.link;
            }
            return window.location.href;
          });
      }
      return this.getUrlForAcquired.apply(this, param_list);
    })

    .declareMethod("render", function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_list'),
            gadget.getSetting("portal_type")
          ]);
        })
        .push(function (result) {
          var column_list = [
            ['message', 'Message'],
            ['created_time', 'Creation Time']
          ];
          return result[0].render({
            erp5_document: {"_embedded": {"_view": {
              "listbox": {
                "column_list": column_list,
                "show_anchor": 0,
                "default_params": {},
                "editable": 1,
                "editable_column_list": [],
                "key": "field_listbox",
                "lines": 30,
                "list_method": "portal_catalog",
                "query": "",
                "portal_type": [],
                "search_column_list": column_list,
                "sort_column_list": column_list,
                "sort": [['created_time', 'descending']],
                "title": "Documents",
                "type": "ListBox"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
            form_definition: {
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getSetting('document_title_plural');
        })
        .push(function (result) {
          return gadget.updateHeader({
            page_title: result,
            filter_action: true
          });
        });
    });
}(window, rJS, RSVP));