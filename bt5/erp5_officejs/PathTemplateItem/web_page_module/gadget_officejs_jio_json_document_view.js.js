/*global window, rJS, RSVP, jIO, URL, Query,
  promiseEventListener, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, jIO, rJS, RSVP, Query) {
  "use strict";

  rJS(window)
  /////////////////////////////////////////////////////////////////
  // Acquired methods
  /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.changeState({
        jio_key: options.jio_key,
        doc: options.doc
      });
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
          var list = [],
            blob;
          if (content.file) {
            blob = jIO.util.dataURItoBlob(content.file.url);
            content.title = content.file.file_name;
            delete content.file;
            list = [
              gadget.updateDocument(content),
              gadget.jio_putAttachment(gadget.state.jio_key, 'data', blob)
            ];
          } else if (content.data) {
            blob = new Blob([content.data]);
            delete content.data;
            list = [
              gadget.updateDocument(content),
              gadget.jio_putAttachment(gadget.state.jio_key, 'data', blob)
            ];
          } else {
            list = [gadget.updateDocument(content)];
          }
          return RSVP.all(list);
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
        }, function (error) {
          if (error.target && error.target.error.name === 'NotReadableError') {
            return gadget.notifySubmitted({message: error.target.error.message, status: 'fail'});
          }
          throw error;
        }).push(function () {
          // debugger;
          return gadget.redirect({
            command: 'reload'
          });
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .allowPublicAcquisition("downloadJSON", function (arr) {
      var g = this,
        url = arr[0],
        reference,
        args;
      if (url.startsWith("urn:jio:reference?")) {
        reference = decodeURIComponent(url.replace("urn:jio:reference?", ""));
        args = {
          query: Query.objectToSearchText({
            type: "complex",
            operator: "AND",
            query_list: [
              {
                key: "portal_type",
                type: "simple",
                value: "JSON Schema"
              },
              {
                key: "reference",
                type: "simple",
                value: reference
              }
            ]
          }),
          limit: [0, 1],
          select_list: [],
          sort_on: [["modification_date", "descending"]]
        };
        return g.jio_allDocs(args)
          .push(function (result) {
            return g.jio_getAttachment(result.data.rows[0].id, "data", {format: "json"});
          });
      }
    })

    .onStateChange(function () {
      var gadget = this,
        schema_obj;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_view'),
            gadget.jio_getAttachment(gadget.state.jio_key, 'data', {format: "json"}),
            gadget.jio_get(gadget.state.doc.schema)
          ]);
        })
        .push(function (result) {
          schema_obj =  result[2];
          return result[0].render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "my_title": {
                    "description": "",
                    "title": "Title",
                    "default": gadget.state.doc.title,
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "title",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "my_file": {
                    "description": "",
                    "title": "Upload and rewrite this document",
                    "default": "",
                    "css_class": "",
                    "required": 0,
                    "editable": 1,
                    "key": "file",
                    "hidden": 0,
                    "accept": "application/json",
                    "type": "FileField"
                  },
                  "my_content": {
                    "default": result[1],
                    "css_class": "",
                    "required": 0,
                    "editable": 1,
                    "key": "data",
                    "hidden": 0,
                    "type": "GadgetField",
                    "renderjs_extra": '{"name": "data",' +
                    ' "schema_url": "urn:jio:reference?' + schema_obj.reference + '"}',
                    "url": "jsonform.gadget.html",
                    "sandbox": "public"
                  }
                }
              },
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
                [["my_title"], ["my_reference"]]
              ], [
                "bottom",
                [["my_content"]]
              ]]
            }
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'display', options: {
                page: "ojs_schema_document_list",
                portal_type: "JSON Document",
                schema: gadget.state.doc.schema,
                schema_title: schema_obj.title
              }}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: gadget.state.doc.title,
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });
    });
}(window, jIO, rJS, RSVP, Query));
