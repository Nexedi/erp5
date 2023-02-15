/*global window, rJS, jIO, navigator, Handlebars, RSVP, Blob, SimpleQuery, ComplexQuery, Query*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS, jIO, navigator,
          RSVP, SimpleQuery, ComplexQuery, Query) {
  "use strict";
  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i, date, len = result.data.total_rows;
          for (i = 0; i < len; i += 1) {
            if (result.data.rows[i].value.hasOwnProperty("modification_date")) {
              date = new Date(result.data.rows[i].value.modification_date);
              result.data.rows[i].value.modification_date = {
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
            }
          }
          return result;
        });
    })

    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .declareMethod("send", function (scope) {
      var gadget = this,
        blob,
        name,
        portal_type = gadget.props.portal_type,
        parent_relative_url = gadget.props.parent_relative_url;

      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget(scope);
        })
        .push(function (form) {
          return form.getContent();
        })
        .push(function (result) {
          if (scope === "form_view_upload_audio" && result.upload) {
            blob = jIO.util.dataURItoBlob(result.upload.url);
            portal_type = portal_type[3];
            parent_relative_url = parent_relative_url[3];
            name = result.upload.file_name;
          } else if (scope === "form_view_image_text" && result.image) {
            blob = jIO.util.dataURItoBlob(result.image.url);
            portal_type = portal_type[1];
            parent_relative_url = parent_relative_url[1];
            name = result.image.file_name;
          }
          if (blob) {
            return gadget.notifySubmitting()
              .push(function () {
                return gadget.jio_post({
                  "title": name,
                  portal_type: portal_type,
                  parent_relative_url: parent_relative_url,
                  state: 'draft'
                });
              })
              .push(function (id) {
                return gadget.jio_putAttachment(id, 'data', blob);
              })
              .push(function () {
                return gadget.notifySubmitted({
                  "message": "Data created",
                  "status": "success"
                });
              })
              .push(function () {
                return gadget.redirect({
                  command: 'display',
                  options: {page: "ojs_smart_assistant_document_list"}
                });
              });
          }
        });
    })
    .allowPublicAcquisition('notifyChange', function (result, scope) {
      /*jslint unparam: true*/
      if (result[0] === "change") {
        return this.send(scope);
      }
    })


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .ready(function (g) {
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.getSetting('portal_type'),
            g.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          g.props = {
            portal_type: result[0].split(','),
            parent_relative_url: result[1].split(',')
          };
        });
    })
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.getSetting('jio_storage_name')
        .push(function (result) {
          if (!result) {
            return gadget.redirect({command: 'display',
                                    options: {page: 'ojs_configurator'}});
          }
          if ('serviceWorker' in navigator) {
            if (navigator.serviceWorker.controller) {
              return jIO.util.ajax({
                url: 'hasSharedData'
              });
            }
          }
        })
        .push(function (result) {
          if (result) {
            if (result.target.response === 'true') {
              return gadget.redirect({command: 'display', options: {
                page: 'ojs_smart_assistant_upload_shared_file'
              }});
            }
          }
          return RSVP.all([
            gadget.getDeclaredGadget('form_view_upload_audio'),
            gadget.getDeclaredGadget('form_view_image_text'),
            gadget.getDeclaredGadget('form_list'),
            gadget.getDeclaredGadget('worklist'),
            gadget.getSetting("portal_type")
          ]);
        })
        .push(function (result) {
          var column_list = [
            ['agent_title', 'Title'],
            ['description', 'Reply'],
            ['modification_date', 'Modification Date'],
            ['state', 'Validation State']
          ],

            worklist_gadget = result[3],
            portal_type = ["Query"],
            query = "urn:jio:allDocs?query=",
            i,
            jio_query_list = [];

          for (i = 0; i < portal_type.length; i += 1) {
            jio_query_list.push(new SimpleQuery({
              key: "portal_type",
              operator: "",
              type: "simple",
              value: portal_type[i]
            }));
          }

          query += Query.objectToSearchText(new ComplexQuery({
            operator: "OR",
            query_list: jio_query_list,
            type: "complex"
          }));

          return RSVP.all([
            worklist_gadget.render(),

            result[0].render({
              erp5_document: {"_embedded": {"_view": {
                "upload": {
                  "editable": 1,
                  "key": "upload",
                  "css_class":
                    "ui-view-only-label ui-label-circle ui-label-icon-files-o",
                  "title": " ",
                  "type": "FileField"
                },
                "audio": {
                  "editable": 1,
                  "required": 1,
                  "key": "",
                  "css_class": "invisible ui-a-circle ui-a-icon-microphone",
                  "default": {"target": "ojs_smart_assistant_audio",
                              "target_type": "audio"},
                  "title": " ",
                  "url": "gadget_erp5_page_ojs_link_field.html",
                  "type": "GadgetField"
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
                  "left",
                  [["upload"]]
                ], [
                  "right",
                  [["audio"]]
                ]]
              }
            }),

            result[1].render({
              erp5_document: {"_embedded": {"_view": {
                "image": {
                  "editable": 1,
                  "key": "image",
                  "css_class":
                    "ui-view-only-label ui-label-circle ui-label-icon-camera",
                  "capture": "camera",
                  "title": " ",
                  "accept": "image/*",
                  "type": "FileField"
                },
                "text": {
                  "editable": 1,
                  "required": 1,
                  "key": "",
                  "css_class":
                    "invisible ui-a-circle ui-a-icon-pencil-square-o",
                  "title": " ",
                  "default": {"target": "smart_assistant_text",
                              "target_type": "text"},
                  "url": "gadget_erp5_page_ojs_link_field.html",
                  "type": "GadgetField"
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
                  "left",
                  [["image"]]
                ], [
                  "right",
                  [["text"]]
                ]]
              }
            }),

            result[2].render({
              erp5_document: {
                "_embedded": {"_view": {
                  "listbox": {
                    "column_list": column_list,
                    "show_anchor": 0,
                    "default_params": {},
                    "editable": 1,
                    "editable_column_list": [],
                    "key": "field_listbox",
                    "lines": 10,
                    "list_method": "portal_catalog",
                    "query": query,
                    "portal_type": [],
                    "search_column_list": column_list,
                    "sort_column_list": column_list,
                    "sort": [['state', 'descending'],
                             ['modification_date', 'descending']],
                    "title": "Notification",
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
            })
          ]);
        })
        .push(function () {
          return RSVP.all([
            gadget.getSetting('document_title_plural'),
            gadget.getUrlFor({command: 'display',
                              options:
                              {page: "ojs_smart_assistant_document_list"}
                             })
          ]);
        })
        .push(function (list_url) {
          return gadget.updateHeader({
            page_title: list_url[0],
            selection_url: list_url[1],
            page_icon: "exchange"
          });
        });
    });

}(window, rJS, jIO, navigator, RSVP, SimpleQuery, ComplexQuery, Query));