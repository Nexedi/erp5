/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var latitude = "";
  var longitude = "";
  var geo_watch_id;

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (doc) {
          if (!doc.car) {
            return new RSVP.Queue().push(function () {
              // Workaround, find a way to open document without break gadget.
              return gadget.redirect({"command": "change", "options": {"page": "drive_app_car"}});
            });
          }
          var now = new Date();
          doc.drive_date = now.getFullYear() + "/" + ("0" + (now.getMonth() + 1)).slice(-2) + "/" + ("0" + now.getDate()).slice(-2) + " " + ("0" + now.getHours()).slice(-2) + ":" + ("0" + now.getMinutes()).slice(-2) + ":" + ("0" + now.getSeconds()).slice(-2);
          doc.modification_date = (new Date()).toISOString();
          doc.distance = 0;
          if (doc.start && doc.end) {
            doc.distance = parseInt(doc.end, 10) - parseInt(doc.start, 10);
            doc.end = parseInt(doc.end, 10);
            doc.start = parseInt(doc.start, 10);
          }
          doc.car_relative_url = doc.car.split('#', 1)[0];
          doc.car_title = doc.car.slice(doc.car_relative_url.length + 1);

          if (doc.sync_flag === "1") {
            doc.portal_type = "Drive Record";
            doc.parent_relative_url = "drive_record_module";
          } else {
            doc.portal_type = "Drive Record Temp";
            doc.parent_relative_url = "";
          }

          // XXXX I don't know why it is here.
          delete doc.default_sync_flag;

          // Geo location
          doc.latitude = latitude;
          doc.longitude = longitude;
          if (navigator.geolocation) {
            navigator.geolocation.clearWatch(geo_watch_id);
          }

          return gadget.jio_post(doc);
        })
        .push(function () {
          // Workaround, find a way to open document without break gadget.
          return gadget.redirect({"command": "change", "options": {"page": "drive_app_document_list"}});
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
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this;

      // Current position
      if (navigator.geolocation) {
        geo_watch_id = navigator.geolocation.watchPosition(function (position) {
          latitude = position.coords.latitude;
          longitude = position.coords.longitude;
        });
      }

      return gadget.getSetting('car')
        .push(function (car_base_value) {
          if (!car_base_value) {
            return new RSVP.Queue().push(function () {
              // Workaround, find a way to open document without break gadget.
              return gadget.redirect({"command": "change", "options": {"page": "drive_app_car"}});
            });
          }
          var car_relative_url = car_base_value.split('#', 1)[0];
          return RSVP.all([
            gadget.getDeclaredGadget('form_view'),
            gadget.getSetting('car'),
            gadget.jio_allDocs({
              query: 'portal_type: ("Drive Record" OR "Drive Record Temp") AND car_relative_url: "' + car_relative_url + '"',
              select_list: ["end"],
              sort_on: [['end', 'descending']],
              limit: [0, 1]
            })
          ]);
        })
        .push(function (result) {
          var car_base_value = result[1] || "";
          var car = car_base_value.split('#', 1)[0];
          var car_title = car_base_value.slice(car.length + 1);
          var sr = result[2];
          var start = "0";
          if (sr.data.total_rows > 0) {
            start = sr.data.rows[0].value.end;
          }
          return result[0].render({
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
                  "default": 0,
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
                  "default": "0",
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
                  "default": "",
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
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "comment",
                  "hidden": 0,
                  "type": "TextAreaField"
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
                "my_car": {
                  "description": "",
                  "title": "Car",
                  "default": car_base_value || "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "car",
                  "hidden": 1,
                  "type": "StringField"
                },
                "my_sync_flag": {
                  "description": "",
                  "title": "Sync?",
                  "default": "0",
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
                [["my_end"], ["my_start"], ["my_distance"], ["my_drive_hour"], ["my_comment"], ["my_car_title"], ["my_car"], ["my_sync_flag"]]
              ]]
            }
          });
        })
        .push(function () {
          gadget.element.querySelector('input[name=distance]').readOnly = true;
          return new RSVP.Queue();
        })
        .push(function () {
          return gadget.getSetting('document_title');
        })
        .push(function (document_title) {
          return gadget.updateHeader({
            page_title: "New " + document_title,
            save_action: true
          });
        });
    });
}(window, rJS, RSVP));