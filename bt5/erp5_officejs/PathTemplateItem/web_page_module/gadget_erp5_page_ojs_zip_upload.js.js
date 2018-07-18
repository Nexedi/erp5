/*global window, rJS, RSVP, loopEventListener,
  jIO, document */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP) {
  "use strict";

  var content_type = {
    Spreadsheet: 'application/x-asc-spreadsheet',
    Presentation: 'application/x-asc-presentation',
    Text: 'application/x-asc-text'
  };

  function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
  }

  function generateMetadata(id, filename, path, body) {
    // it's core of upload of zip gadget
    // in this function can be added support another formats
    var ret;
    if (endsWith(filename, ".json")) {
      ret = {
        id: id,
        content_type: "application/json",
        reference: path
      };
      if (body) {
        if (body.$schema && body.$schema !== "") {
          ret.portal_type = "JSON Schema";
          ret.parent_relative_url = "schema_module";
          ret.title = body.title || "";
        } else {
          // XXX need schema relation property
          ret.portal_type = "JSON Document";
          ret.parent_relative_url = "document_module";
          ret.title = body.filename || "";
        }
      } else {
        ret.format = "json";
      }
      // used for detect supported extension
      return ret;
    }
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.changeState({
        title: 'Untitled Document'
      });
    })

    .declareMethod('putIntoDB', function (id, file_name, path, blob) {
      var gadget = this,
        queue = RSVP.Queue(),
        // first run generateMetadata for check file support
        // and detect document format
        file_supported = generateMetadata(id, file_name, path);
      if (file_supported) {
        if (file_supported.format === "json") {
          queue
            .push(function () {
              return jIO.util.readBlobAsText(blob);
            })
            .push(function (evt) {
              return JSON.parse(evt.target.result);
            });
        } else {
          queue.push(function () {
            return blob;
          });
        }
        queue
          .push(function (data) {
            return gadget.jio_post(generateMetadata(id, file_name, path, data))
              .push(function (added_id) {
                return gadget.jio_putAttachment(added_id, 'data', blob);
              });
          });
      }
      return queue;
    })

    .declareMethod('triggerSubmit', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          return new RSVP.Queue()
            .push(function () {
              return RSVP.all([
                gadget.getSetting('jio_storage_name'),
                gadget.getSetting('jio_storage_description')
              ]);
            })
            .push(function (result) {
              var promiseArray = [],
                data_array = content.data,
                i,
                blob,
                storage_name = result[0],
                storage_description = result[1],
                storage,
                local_database,
                configuration;

              // XXX support other type of storage
              if (storage_name === "LOCAL") {
                local_database = storage_description.sub_storage.sub_storage.database;
              }

              for (i = 0; i < data_array.length; i += 1) {
                blob = jIO.util.dataURItoBlob(data_array[i].url);
                if (endsWith(data_array[i].file_name, ".zip")) {
                  configuration = {
                    type: "replicate",
                    conflict_handling: 2,
                    check_local_attachment_creation: false,
                    check_local_creation: false,
                    check_local_modification: false,
                    check_local_deletion: false,
                    check_remote_attachment_creation: true,
                    check_remote_creation: true,
                    check_remote_modification: true,
                    check_remote_deletion: true,
                    local_sub_storage: {
                      type: "indexeddb",
                      database: local_database
                    },
                    signature_sub_storage: {
                      type: "query",
                      sub_storage: {
                        type: "memory"
                      }
                    },
                    remote_sub_storage: {
                      type: "ziptodocuments",
                      generateMetadata: generateMetadata,
                      sub_storage: {
                        type: "zipfile",
                        file: blob
                      }
                    }
                  };
                  storage = jIO.createJIO(configuration);
                  promiseArray.push(storage.repair());
                } else {
                  promiseArray.push(gadget.putIntoDB("", data_array[i].file_name, data_array[i].file_name, blob));
                }
              }
              return RSVP.all(promiseArray);
            });
        })
        .push(function () {
          return RSVP.all([
            gadget.notifySubmitted({message: 'Data Updated', status: 'success'}),
            gadget.redirect({command: 'history_previous'})
          ]);
        });
    })

    .onStateChange(function () {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_view'),
            gadget.getSetting('upload_content_type')
          ]);
        })
        .push(function (result) {
          return result[0].render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "my_file": {
                    "description": "",
                    "title": "Upload files and Zip archive containing files",
                    "default": "",
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "data",
                    "hidden": 0,
                    "multiple": "true",
                    "accept": "application/zip," + result[1],
                    "type": "FileField"
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
                [["my_file"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getUrlFor({command: 'history_previous'});
        })
        .push(function (result) {
          return gadget.updateHeader({
            page_title: 'Document(s)',
            back_field: true,
            selection_url: result,
            save_action: true
          });
        });
    });
}(window, rJS, jIO, RSVP));
