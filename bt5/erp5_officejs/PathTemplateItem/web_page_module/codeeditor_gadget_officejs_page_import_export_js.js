/*globals window, RSVP, rJS, loopEventListener, URL, document
  FileReader, console */
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, jIO) {
  "use strict";

  var map_ext2portal_type = {
      'js': 'Web Script',
      'html': 'Web Page',
      'css': 'Web Style',
      'appcache': 'Web Manifest'
    },
    map_portal_type2content_type = {
      'Web Script': 'application/javascript',
      'Web Page': 'text/html',
      'Web Style': 'text/css',
      'Web Manifest': 'text/cache-manifest'
    };

  function create_file(storage, path, file_name, body) {
    return storage.get(path)
    .push(undefined, function (error) {
      if (error.status_code === 404) {
        return storage.put(path, {});
      }
      throw error;
    })
    .push(function () {
      return storage.putAttachment(path, file_name, body);
    });
  }

  function exportAllDocs(gadget) {
    var storage_type = gadget.props
      .element.querySelector("select[name='storage_type']").value;
    return new RSVP.Queue()
    .push(function () {
      return RSVP.all([
        gadget.getGlobalSetting('document_version'),
        gadget.allDocsArchived({type: storage_type})
      ]);
    })
    .push(function (res_list) {
      var version = res_list[0],
        blob = res_list[1],
        element = gadget.props.element,
        a = document.createElement("a"),
        url = URL.createObjectURL(blob);
      element.appendChild(a);
      a.style = "display: none";
      a.href = url;
      a.download = version + ".zip";
      a.click();
      element.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  function getAllAttachment(storage, callback) {
    return storage.allDocs()
      .push(function (r) {
        return RSVP.all(r.data.rows.map(function (row) {
          var id = row.id;
          return storage.allAttachments(id)
            .push(function (files) {
              return RSVP.all(Object.getOwnPropertyNames(files)
                .map(function (filename) {
                  return storage.getAttachment(id, filename)
                    .push(function (blob) {
                      return callback(id, filename, blob);
                    });
                })
              );
            });
        }));
      });
  }

  function readFile(gadget, e) {
    var file = e.target.files[0],
      file_storage,
      storage_type = "zipfile",
      file_element = e.target,
      display_element = gadget.props.element
        .querySelector('form.import-form #file_load_result');
    gadget.props.file_storage = undefined;
    gadget.props.files_preloaded_for_import = [];
    if (!file) {
      display_element.textContent = "";
      return;
    }
    display_element.textContent = "process file....";
    file_element.disabled = true;
    file_storage = jIO.createJIO({type: storage_type, file: file});
    return getAllAttachment(file_storage, function (path, fn, blob) {
      var url_string,
        portal_type,
        text_content;
      portal_type = map_ext2portal_type[fn.slice(fn.lastIndexOf('.') + 1)];
      if (!portal_type) {
        throw "not supported file format: " + fn;
      }
      if (fn === "index.html") {
        fn = "";
      }
      url_string = path.slice(1) + fn;
      if (url_string === "") {
        url_string = "/";
      }
      gadget.props.files_preloaded_for_import
        .push({id: url_string,
               reference: fn,
               portal_type: portal_type,
               blob: blob
              });
    })
    .push(function () {
      display_element.textContent = storage_type + " contains " +
        gadget.props.files_preloaded_for_import.length +
        " files and ready for import";
      gadget.props.file_storage = file_storage;
    }, function (error) {
      display_element.textContent = "file processing error: " + error;
    })
    .push(function () {
      file_element.disabled = false;
    });
  }

  function importAllDocs(gadget) {
    var files = gadget.props.files_preloaded_for_import;
    if (gadget.props.files_preloaded_for_import.lenght === 0) {
      return;
    }
    return new RSVP.Queue()
      .push(function () {
        return gadget.getGlobalSetting('document_version');
      })
      .push(function (version) {
        return RSVP.all(files.map(function (file) {
          var text_content;
          return new RSVP.Queue()
            .push(function () {
              return jIO.util.readBlobAsText(file.blob);
            })
            .push(function (result) {
              text_content = result.target.result;
              return gadget.jio_get(file.id);
            })
            .push(undefined, function (error) {
              if (error.status_code === 404) {
                return false;
              }
              throw error;
            })
            .push(function (obj) {
              if (obj === false || obj.content_type === "blob") {
                obj = {
                  portal_type: file.portal_type,
                  content_type:
                    map_portal_type2content_type[file.portal_type],
                  parent_relative_url: "web_page_module",
                  version: version,
                  reference: file.reference
                };
              } else {
                if (obj.portal_type !== file.portal_type) {
                  throw "existed document " + file.id +
                    " have incorrect portal_type";
                }
                if (obj.text_content === text_content) {
                  return;
                }
              }
              obj.text_content = text_content;
              console.log(file.id + ": save file");
              return gadget.jio_put(file.id, obj);
            });
        }));
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareMethod("getGlobalSetting", function (key) {
      var gadget = this;
      return gadget.getDeclaredGadget("global_setting_gadget")
        .push(function (global_setting_gadget) {
          return global_setting_gadget.getSetting(key);
        });
    })
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareMethod("allDocsArchived", function (opt) {
      var gadget = this,
          file_storage = jIO.createJIO(opt);
      return this.jio_allDocs({select_list: ["reference", "text_content"]})
      .push(function (result) {
        var i,
          len,
          data = result.data,
          row,
          idx,
          path,
          file_name,
          text_content,
          promises = [];
        for (i = 0, len = data.total_rows; i < len; i += 1) {
          row = data.rows[i];
          path = row.id;
          if (path === "") {
            path = row.value.reference;
          }
          idx = path.lastIndexOf('/');
          if (idx != -1) {
            file_name = path.slice(idx + 1);
            path = "/" + path.slice(0, idx);
            if (file_name === "") {
              file_name = "index.html";
            }
            if (path.slice(-1) !== "/") {
              path = path + "/";
            }
          } else {
            file_name = path;
            path = "/";
          }
          text_content = row.value.text_content;
          if (text_content) {
            promises.push(create_file(file_storage,
                                      path,
                                      file_name,
                                      text_content));
          }
        }
        return RSVP.all(promises);
      })
      .push(function () {
        return file_storage.getAttachment('/', '/');
      });
    })
//     .declareMethod("render", function (options) {
//       var gadget = this;
//       return gadget.updateHeader({
//         title: "Connect To ERP5 Storage",
//         back_url: "#page=jio_code_editor_configurator",
//         panel_action: false
//       })
//         .push(function () {
//           return gadget.getSetting('jio_storage_name');
//         })
//         .push(function (jio_storage_name) {
//           if (!jio_storage_name) {
//             gadget.props.element.querySelector(".document-access").setAttribute("style", "display: none;");
//           }
//         })
//         .push(function () {
//           return gadget.props.deferred.resolve();
//         });


//       var gadget = this;
//       return new RSVP.Queue()
//         .push(function () {
//           return RSVP.all([
//             gadget.getSetting("portal_type"),
//             gadget.getSetting("document_title_plural")
//           ]);
//         })
//         .push(function (answer_list) {
//           gadget.props.portal_type = answer_list[0];
//           gadget.props.document_title_plural = answer_list[1];
//           return gadget.getUrlFor({page: "add_document"});
//         })
//         .push(function (url) {
//           return gadget.updateHeader({
//             title: gadget.props.document_title_plural,
//             add_url: url
//           });
//         })
//         .push(function () {
//           return gadget.getDeclaredGadget("listbox");
//         })
//         .push(function (listbox) {
//           return listbox.render({
//             search_page: 'document_list',
//             search: options.search,
//             column_list: [{
//               select: 'title',
//               title: 'Title'
//             }, {
//               select: 'url_string',
//               title: 'Url String'
//             }, {
//               select: 'language',
//               title: 'Language'
//             }, {
//               select: 'description',
//               title: 'Description'
//             }, {
//               select: 'version',
//               title: 'version'
//             }, {
//               select: 'modification_date',
//               title: 'Modification Date'
//             }],
//             query: {
//               query: 'portal_type:("Web Page","Web Script","Web Manifest","Web Style")',
//               select_list: ['title', 'url_string', 'language',
//                             'description', 'version', 'modification_date'],
//               limit: [0, 1234567890],
//               sort_on: [["modification_date", "descending"]]
//             }
//           });
//         });
//     })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getSetting("global_setting_gadget_url");
        })
        .push(function (global_setting_gadget_url) {
          return gadget.declareGadget(
            global_setting_gadget_url,
            {
              scope: "global_setting_gadget",
              sandbox: "iframe",
              element: gadget.props.element.querySelector("#global_setting_gadget")
            }
          );
        })
        .push(function () {
          return RSVP.all([
            loopEventListener(
              gadget.props.element.querySelector('form.export-form'),
              'submit',
              true,
              function () {
                return exportAllDocs(gadget);
              }
            ),
            loopEventListener(
              gadget.props.element.querySelector('form.import-form input#file'),
              'change',
              true,
              function (e) {
                return readFile(gadget, e);
              }
            ),
            loopEventListener(
              gadget.props.element.querySelector('form.import-form'),
              'submit',
              true,
              function () {
                return importAllDocs(gadget);
              }
            )
          ]);
        });
    });

}(window, RSVP, rJS, jIO));