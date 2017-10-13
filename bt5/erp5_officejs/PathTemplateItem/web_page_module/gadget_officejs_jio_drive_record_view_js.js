/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      return this.changeState({
        jio_key: options.jio_key,
        doc: options.doc
      });
    })
    .onEvent('change', function (event) {
      var gadget = this;

      if (event.target.getAttribute('name') === 'start' || event.target.getAttribute('name') === 'end') {
        var start_input = gadget.element.querySelector('input[name=start]');
        var end_input = gadget.element.querySelector('input[name=end]');
        var distance_value = 0;
        if (start_input.value && end_input.value) {
          distance_value = parseInt(end_input.value, 10) - parseInt(start_input.value, 10);
        }
        var distance_input = gadget.element.querySelector('input[name=distance]');
        distance_input.value = distance_value;
      }
    })
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          var doc;
          doc = gadget.state.doc;
          doc.start = parseInt(content.start, 10);
          doc.end = parseInt(content.end, 10);
          doc.distance = 0;
          if (content.start && content.end) {
            doc.distance = parseInt(content.end, 10) - parseInt(content.start, 10);
          }
          doc.drive_hour = parseInt(content.drive_hour, 10);
          doc.comment = content.comment;
          doc.modification_date = (new Date()).toISOString();
          doc.sync_flag = content.sync_flag;
          if (content.sync_flag === "1") {
            doc.portal_type = "Drive Record";
            doc.parent_relative_url = "drive_record_module";
          } else {
            doc.portal_type = "Drive Record Temp";
            doc.parent_relative_url = "";
          }

          // XXXX I don't know why it is here.
          delete doc.default_sync_flag;

          return gadget.jio_put(gadget.state.jio_key, doc);
        })
        .push(function () {
          return RSVP.all([
            gadget.notifySubmitted('Data Updated')
          ]);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          var editable = gadget.state.editable;
          var car_title = gadget.state.doc.car_title;
          var start = gadget.state.doc.start.toString();
          var end = gadget.state.doc.end.toString();
          var distance = gadget.state.doc.distance.toString();
          var drive_hour = (gadget.state.doc.drive_hour || "0").toString();
          var comment = gadget.state.doc.comment || "";
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_start": {
                  "description": "",
                  "title": "Start",
                  "default": start,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "start",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_end": {
                  "description": "",
                  "title": "End",
                  "default": end,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "end",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_distance": {
                  "description": "",
                  "title": "Distance",
                  "default": distance,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "distance",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_drive_hour": {
                  "description": "",
                  "title": "Drive Hours",
                  "default": drive_hour,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "drive_hour",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_comment": {
                  "description": "",
                  "title": "Comment",
                  "default": comment,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "comment",
                  "hidden": 0,
                  "type": "TextAreaField"
                },
                "my_drive_date": {
                  "description": "",
                  "title": "Drive Date",
                  "default": gadget.state.doc.drive_date,
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "drive_date",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_car_title": {
                  "description": "",
                  "title": "Car",
                  "default": car_title,
                  "css_class": "",
                  "required": 0,
                  "editable": 0,
                  "key": "car_title",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_sync_flag": {
                  "description": "",
                  "title": "Sync?",
                  "default": gadget.state.doc.sync_flag,
                  "items": [["YES", "1"], ["NO", "0"]],
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "sync_flag",
                  "hidden": 0,
                  "type": "RadioField"
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
                [["my_end"], ["my_start"], ["my_distance"], ["my_drive_hour"], ["my_comment"], ["my_drive_date"], ["my_car_title"], ["my_sync_flag"] ]
              ]]
            }
          });
        })
        .push(function () {
          gadget.element.querySelector('input[name=distance]').readOnly = true;
          return new RSVP.Queue();
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (url_list) {
          var save_action = true;
          if (gadget.state.jio_key.lastIndexOf("drive_record_module/") === 0) {
            save_action = false;
            gadget.element.querySelectorAll('input').forEach(function (item) {item.readOnly = true; });
          }
          var header_dict = {
            page_title: gadget.state.doc.jio_key,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          };
          if (save_action) {
            header_dict.save_action = true;
          }
          return gadget.updateHeader(header_dict);
        });
    });
}(window, rJS, RSVP));
