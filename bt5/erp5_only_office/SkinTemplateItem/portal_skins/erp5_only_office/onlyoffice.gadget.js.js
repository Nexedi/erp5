/*global window, rJS, RSVP, DocsAPI, console, document,
 Common, AscCommon, require, jIO, URL, FileReader, atob, ArrayBuffer,
 Uint8Array, XMLHttpRequest, Blob, Rusha, define,
 Uint8ClampedArray, Asc, History,
 TextDecoder, DesktopOfflineAppDocumentEndSave*/
/*jslint nomen: true, maxlen:80, indent:2*/
"use strict";
if (Common === undefined) {
  var Common = {};
}
var DocsAPI = {DocEditor: {}};
DocsAPI.DocEditor.version = function () {
  return null;
};

(function (rJS, RSVP, require, jIO) {

  var rusha = new Rusha();

  function hexdigest(blob) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.readBlobAsArrayBuffer(blob)
          .then(function (evt) {
            return rusha.digest(evt.target.result);
          });
      });
  }

  function display_error(gadget, error) {
    var display_error_element;
    display_error_element = gadget.props.element;
    display_error_element.innerHTML =
      '<br/><p style="color: red"></p><br/><br/>';
    display_error_element.querySelector('p').textContent = error;
    console.error(error);
    throw error;
  }

  function dataURLtoBlob(url) {
    if (url === 'data:') {
      return new Blob();
    }
    var byteString = atob(url.split(',')[1]),
      mimeString = url.split(',')[0].split(':')[1].split(';')[0],
      ab = new ArrayBuffer(byteString.length),
      ia = new Uint8Array(ab),
      i;
    for (i = 0; i < byteString.length; i += 1) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], {type: mimeString});
  }

  function printOlapTable(xmla_client, data) {
    var Api = Asc.editor,
      s = Api.GetActiveSheet(),
      connection_name,
      start_row,
      start_column;

    function endTransaction() {
      s.worksheet.workbook.dependencyFormulas.unlockRecal();
      History.EndTransaction();
      Api._onUpdateAfterApplyChanges();
      Api._onUpdateDocumentCanSave();
    }

    function setCell(row, col, value, row1, col1) {
      // setValue on range
      s.GetRangeByNumber(row, col).range._foreach(function (cell) {
        cell.setValue(value);
      });
      if (typeof row1 === "number" && typeof col1 === "number") {
        var range = s.worksheet.getRange3(row, col, row1, col1);
        if (col1 !== col) {
          range.setAlignHorizontal(AscCommon.align_Center);
        }
        if (row1 !== row) {
          range.setAlignVertical(Asc.c_oAscVAlign.Top);
        }
        s.worksheet.mergeManager.add(range.bbox, 1);
      }
    }

    function print_titles(levels, begin_row, begin_column, columns) {
      var members = [],
        member,
        i,
        m,
        col1,
        row1,
        func,
        x,
        z,
        row,
        col,
        span,
        repeats;

      function amp_arr_length(amp, arr) {
        if (arr.length === 0) {
          return amp;
        }
        return amp * arr.length;
      }

      for (i = 0; i < levels.length; i += 1) {
        members = levels[i];
        span = levels.slice(i + 1).reduce(amp_arr_length, 1);
        repeats = levels.slice(0, i).reduce(amp_arr_length, 1);
        for (z = 0; z < repeats * members.length * span; z += (members.length * span)) {
          for (m = 0; m < members.length; m += 1) {
            member = members[m];
            func = "=CUBEMEMBER(" + connection_name + ',"' + member.uname + '")';
            for (x = 1; x < span; x += 1) {
              if (columns) {
                row = begin_row + i;
                col = begin_column + z + (m * span) + x;
              } else {
                row = begin_row + z + (m * span) + x;
                col = begin_column + i;
              }
              setCell(row, col, func);
            }
            if (columns) {
              row = begin_row + i;
              col = begin_column + z + (m * span);
              if (span > 1) {
                row1 = row;
                col1 = col + span - 1;
              } else {
                row1 = undefined;
                col1 = undefined;
              }
            } else {
              row = begin_row + z + (m * span);
              col = begin_column + i;
              if (span > 1) {
                row1 = row + span - 1;
                col1 = col;
              } else {
                row1 = undefined;
                col1 = undefined;
              }
            }
            setCell(row, col, func, row1, col1);
          }
        }
      }
      return repeats * members.length * span;
    }

    if (!data.connection_name) {
      return;
    }

    return RSVP.Queue()
      .push(function () {
        // var active = s.GetActiveCell();
        // var row = active.GetRow();
        // var col = active.GetCol();
        start_row = 0;
        start_column = 0;
        History.Create_NewPoint();

        s.worksheet.workbook.dependencyFormulas.lockRecal();


        // XXX use named ranges for cleaning space
        s.worksheet.getRange3(0, 0, 10000, 10000).cleanAll();
        // (new Asc.asc_CDefName(
        //   "name111",
        //   "Sheet1!$A$3:$D$13",
        //   null, // or number of sheet
        //   this.props.asc_getIsTable(),
        //   false, // Hidden
        //   false // locked
        // ));
        // rows titles

        setCell(start_row, start_column, "Connection:");
        setCell(start_row, start_column + 1, data.connection_name);
        connection_name = "$B$1";
        start_row += 2;

        // XXX default absent in json schema
        data.rows = data.rows || [];
        data.columns = data.columns || [];

        return RSVP.all([
          RSVP.all(data.rows
            .filter(function (i) {
              return i.hasOwnProperty("level");
            })
            .map(function (i) {
              return xmla_client
                .getMembersOnLevel(data.connection_name, i.level);
            })),
          RSVP.all(data.columns
            .filter(function (i) {
              return i.hasOwnProperty("level");
            })
            .map(function (i) {
              return xmla_client
                .getMembersOnLevel(data.connection_name, i.level);
            }))
        ]);
      })
      .push(function (arr) {
        var rows = arr[0],
          columns = arr[1],
          c,
          c_len,
          r,
          r_len,
          formula;

        r_len = print_titles(rows, start_row + columns.length, start_column, false);
        c_len = print_titles(columns, start_row, start_column + rows.length, true);

        r_len = r_len + start_row + columns.length;
        c_len = c_len + start_column + rows.length;
        for (r = start_row + columns.length; r < r_len; r += 1) {
          for (c = start_column + rows.length; c < c_len; c += 1) {
            formula = "CUBEVALUE(" + connection_name + ',' +
            s.worksheet.getRange3(r, start_column, r, start_column + rows.length -1).getName() +
            ',' +
            s.worksheet.getRange3(start_row, c, start_row + columns.length - 1, c).getName() +
            ')';
            setCell(r, c,
              "=IF(ISTEXT(" + formula + '),0,' + formula + ')');
          }
        }

        endTransaction();
      })
      .push(undefined, function (error) {
        endTransaction();
        throw error;
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {
        save_defer: null,
        handlers: {},
        headerCaption: ""
      };
    })
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          return {};
        });
    })
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .declareAcquiredMethod("triggerMaximize", "triggerMaximize")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('notifyChange', 'notifyChange')
    .declareMethod("jio_getAttachment", function (docId, attId, opt) {
      var g = this,
        convert;
      opt = opt || {};
      if (attId === 'body.txt' || attId === 'Editor.bin') {
        opt = { 'format': 'bin_array' };
        if (!docId) {
          docId = '/';
        }
      } else {
        if (!docId) {
          docId = '/media/';
        }
      }
      if (opt.format === "blob_url") {
        convert = opt.format;
        delete opt.format;
      }
      if (opt.format === "bin_array") {
        convert = opt.format;
        opt.format = 'array_buffer';
      }
      return g.props.value_zip_storage.getAttachment(docId, attId, opt)
        .push(function (blob) {
          if (convert === "bin_array") {
            return new Uint8ClampedArray(blob);
          }
          if (convert === "blob_url") {
            return URL.createObjectURL(blob);
          }
          return blob;
        });
    })
    .declareMethod("jio_putAttachment", function (docId, atId, data) {
      var g = this,
        zip = g.props.value_zip_storage,
        queue,
        content_type,
        start;
      if (!docId) {
        docId = '/media/';
      }
      if (typeof data === 'string') {
        start = data.slice(0, 5);
        if (start === "data:") {
          data = dataURLtoBlob(data);
        }
      }
      if (typeof data === 'object' &&
          !(data instanceof Blob)) {
        data = new Blob([JSON.stringify(data, undefined, 2)]);
      }
      if (atId) {
        queue = zip.putAttachment(docId, atId, data)
          .push(undefined, function (error) {
            if (error.status_code === 404) {
              // make dir
              return zip.put(docId, {})
                .push(function () {
                  return zip.putAttachment(docId, atId, data);
                });
            }
            throw error;
          });
      } else {
        queue = hexdigest(data)
          .push(function (digest) {
            content_type = data.type;
            if (!content_type) {
              content_type = "application/binary";
            }
            content_type = content_type.split('/');
            atId = content_type[0] + ',' + digest +
              '.' + content_type[1];
            return zip.allAttachments(docId)
              .push(undefined, function (error) {
                if (error.status_code === 404) {
                  // make dir
                  return zip.put(docId, {});
                }
                throw error;
              })
              .push(function (list) {
                if (list.hasOwnProperty(atId)) {
                  return {};
                }
                return zip.putAttachment(docId, atId, data);
              });
          })
          .push(function () {
            return atId;
          });
      }
      return queue;
    })
    .allowPublicAcquisition("notifyChange", function (arr, scope) {
      var gadget = this,
        content;
      if (scope === "remote_settings") {
        return this.getDeclaredGadget(scope)
          .push(function (g) {
            return g.getContent();
          })
          .push(function (data) {
            content = data;
            return gadget
              .jio_putAttachment('/', 'remote_settings.json', data);
          })
          .push(function () {
            History.Create_NewPoint();
            Asc.editor._onUpdateDocumentCanSave();
            return gadget.changeState({changed: true});
          })
          .push(function () {
            return gadget.getDeclaredGadget("xmla_client");
          })
          .push(function (g) {
            return g.setConnectionsSettings(content);
          })
          .push(function () {
            return gadget.getDeclaredGadget("xmlawizard");
          })
          .push(function (g) {
            return g.rerender();
          })
          .push(undefined, function (e) {
            console.error(e);
          });
      }
      if (scope === "xmlawizard") {
        return this.getDeclaredGadget(scope)
          .push(function (g) {
            return RSVP.all([
              gadget.getDeclaredGadget("xmla_client"),
              g.getContent()
            ]);
          })
          .push(function (arr) {
            return printOlapTable(arr[0], arr[1]);
          })
          .push(function () {
            return gadget.changeState({changed: true});
          })
          .push(undefined, function (e) {
            console.error(e);
          });
      }
    })
    .allowPublicAcquisition("getRemoteSettings", function () {
      return this.jio_getAttachment('/', 'remote_settings.json', {format: 'json'})
        .push(undefined, function (error) {
          if (error.status_code === 404) {
            return {};
          }
        });
    })

    // methods emulating Gateway used for connection with ooffice begin.
    .declareMethod('appReady', function () {
      var g = this;
      console.log('appReady');
      return new RSVP.Queue()
        .push(function () {
          g.props.handlers.init({
            config: {
              lang: 'en',
              canAutosave: false,
              canCoAuthoring: false,
              canBackToFolder: true,
              canCreateNew: false,
              canAnalytics: false,
              customization: {
                autosave: false,
                about: false,
                feedback: false
              }
            }
          });
          g.props.handlers.opendocument({
            doc: {
              key: g.props.jio_key,
              //title: g.props.doc.title || "",
              //fileType: undefined,
              //vkey: undefined,
              url: "_offline_",
              permissions: {
                edit: true,
                download: true,
                reader: true
              }
            }
          });
        });
    })
    .declareMethod('documentReady', function () {
      console.log();
    })
    .declareMethod('goBack', function (new_window) {
    })
    .declareMethod('requestEditRights', function () {
      var g = this;
      g.props.handlers.applyEditRights({
        allowed: true,
        message: ""
      });
    })
    .declareMethod('requestHistory', function () {
    })
    .declareMethod('requestHistoryData', function (revision) {
    })
    .declareMethod('requestHistoryClose', function () {
    })
    .declareMethod('reportError', function (code, description) {
      console.log(['reportError', code, description]);
    })
    .declareMethod('sendInfo', function (info) {
      console.log(['sendInfo', info]);
    })
    .declareMethod('setDocumentModified', function (modified) {
    })
    .declareMethod('internalMessage', function (event_name, data) {
      console.log(['internalMessage', event_name, data]);
    })
    .declareMethod('updateVersion', function () {
    })
    .declareMethod('on', function (event_name, handler) {
      var g = this;
      g.props.handlers[event_name] = handler;
    })
    // methods emulating Gateway used for connection with ooffice end.

    .declareMethod('render', function (options) {
      console.log('begin render');
      var g = this,
        queue = new RSVP.Queue();
      return queue
        .push(function () {
          return g.getSetting('portal_type');
        })
        .push(undefined, function (error) {
          return "";
        })
        .push(function (portal_type) {
          var value;
          portal_type = portal_type || options.portal_type;
          g.props.binary_loader = false;
          g.props.jio_key = options.jio_key;
          g.props.key = options.key || "text_content";
          g.props.documentType = portal_type.toLowerCase();
          value = options.value;
          if (value === "data:" ||
            g.props.value === "data:application/octet-stream;base64," ||
            value === undefined) {
            // fix empty value
            value = "";
          }
          if (value) {
            if (value.slice === undefined) {
              throw "not suported type of variable containing the document: " +
                typeof value;
            }
            if (value.slice(0, 5) === "data:") {
              value = atob(value.split(',')[1]);
            }
          }
          if (value) {
            switch (value.slice(0, 4)) {
            case "PK\x03\x04":
            case "PK\x05\x06":
              g.props.value_zip_storage = jIO.createJIO({
                type: "zipfile",
                file: value
              });
              return g.jio_getAttachment('/', 'body.txt')
                .push(undefined, function (error) {
                  if (error.status_code === 404) {
                    return g.jio_getAttachment('/', 'Editor.bin')
                      .push(undefined, function (error) {
                        if (error.status_code === 404) {
                          throw 'not supported format of document:' +
                          ' body.txt/Editor.bin absent "' +
                          value.slice(0, 100) + '"';
                        }
                        throw error;
                      });
                  }
                  throw error;
                });
            }
          }
        })
        .push(function (value) {
          var documentType, magic;
          g.props.value = value;
          if (!g.props.documentType && value === "") {
            throw "can not create empty document " +
            "because portal_type is unknown";
          }
          if (value) {
            magic = value.slice(0, 4);
            if (typeof magic !== 'string') {
              magic = String.fromCharCode.apply(null, magic);
            }
            switch (magic) {
            case 'XLSY':
              documentType = "spreadsheet";
              break;
            case 'PPTY':
              documentType = "presentation";
              break;
            case 'DOCY':
              documentType = "text";
              break;
            default:
              throw "can not detect document type by magic: " + magic;
            }
            if (g.props.documentType) {
              if (documentType !== g.props.documentType) {
                throw "editor not fit the document type";
              }
            } else {
              //set editor type by documentType
              g.props.documentType = documentType;
            }
          }
        })
        .push(function () {
          return new RSVP.Queue()
            .push(function () {
              return jIO.util.ajax({
                type: "GET",
                url: "onlyoffice.gadget.appcache"
              });
            })
            .push(undefined, function (error) {
              return;
            });
        })
        .push(function (response) {
          /*configure requeryjs for rename
          view and edit to view_folder and edit_folder
          in dependencies
          */
          if (!response) {
            return;
          }
          var text = response.target.responseText,
            relative_url_list = text.split('\r\n'),
            i,
            new_url,
            old_url,
            config = {};
          if (relative_url_list.length === 1) {
            relative_url_list = text.split('\n');
          }
          if (relative_url_list.length === 1) {
            relative_url_list = text.split('\r');
          }
          for (i = 0; i < relative_url_list.length; i += 1) {
            if (
              relative_url_list[i] !== "" &&
              relative_url_list[i].charAt(0) !== '#' &&
              relative_url_list[i].charAt(0) !== ' ') {
              relative_url_list[i].replace("\r", "");
              new_url = relative_url_list[i]
                .replace('onlyoffice/web-apps/apps/', '')
                .replace(/\.[^.]*$/, '');
              old_url = new_url
                .replace(/(^|\/)view_folder\//g,"$1view/")
                .replace(/(^|\/)edit_folder\//g,"$1edit/");
              if (old_url !== new_url) {
                config[old_url] = [
                    new_url,
                    old_url
                ];
              }
            }
          }
          require.config({paths: config});
        })
        .push(function () {
          var app_url, sdk_deps = ["promise!sdk_async_loader"];
          if (!g.props.value_zip_storage) {
            g.props.value_zip_storage = jIO.createJIO({type: "zipfile"});
          }
          switch (g.props.documentType) {
          case 'spreadsheet':
            app_url = "web-apps/apps/spreadsheeteditor/main/app.js";
            define("sdk_files", [], function () {
              return "webexcel.json";
            });
            sdk_deps.push('window!Xmla');
            break;
          case 'text':
            app_url = "web-apps/apps/documenteditor/main/app.js";
            define("sdk_files", [], function () {
              return "webword.json";
            });
            break;
          case 'presentation':
            app_url = "web-apps/apps/presentationeditor/main/app.js";
            define("sdk_files", [], function () {
              return "webpowerpoint.json";
            });
            break;
          }

          Common.Gateway = g;

          require.onError = function (error) {
            console.error(error);
          };
          require.config({catchError: true});

          if (g.props.binary_loader) {
            g.props.base_url = "onlyoffice-bin/";
            g.props.headerCaption = "BIN " + g.props.headerCaption;
          } else {
            g.props.base_url = "onlyoffice/";
            define("sdk", sdk_deps, function () {
            });
          }
          app_url = g.props.base_url + app_url;

          function loadScript(src) {
            return new RSVP.Promise(function (resolve, reject) {
              var s;
              s = document.createElement('script');
              s.src = src;
              s.onload = resolve;
              s.onerror = reject;
              document.head.appendChild(s);
            });
          }

          return loadScript(app_url);
        })
        .push(function () {
          return g.getDeclaredGadget("xmla_client");
        })
        .push(function (xmla_client) {
          return xmla_client.render();
        })
        .push(undefined, function (error) {
          display_error(g, error);
        });
    })

    .declareMethod("jio_save", function (data) {
      var g = this,
        zip = g.props.value_zip_storage;
      return new RSVP.Queue()
        .push(function () {
          if (data) {
            return g.jio_putAttachment('/', 'body.txt', data)
              .push(function () {
                // cleanup if Editor.bin exist
                return zip.removeAttachment('/', 'Editor.bin')
                  .push(undefined, function (error) {
                    if (error.status_code !== 404) {
                      throw error;
                    }
                  });
              })
              .push(undefined, function (error) {
                display_error(g, error);
              });
          }
        })
        .push(function () {
          if (g.props.save_defer) {
            // if we are run from getContent
            g.props.save_defer.resolve();
            g.props.save_defer = null;
          } else {
            return g.triggerSubmit();
          }
        });
    })
    .declareMethod('getContent', function () {
      var g = this,
        zip = g.props.value_zip_storage,
        queue = new RSVP.Queue();
      if (g.props.handlers.save()) {
        g.props.save_defer = RSVP.defer();
      }
      return queue.push(function () {
        if (g.props.save_defer) {
          return g.props.save_defer.promise;
        }
      })
        .push(function () {
          // prevent save empty zip archive
          // check document exist in archive
          return zip.getAttachment('/', 'Editor.bin')
            .push(undefined, function (error) {
              if (error.status_code === 404) {
                return zip.getAttachment('/', 'body.txt')
                  .push(undefined, function (error) {
                    if (error.status_code === 404) {
                      return "";
                    }
                    throw error;
                  });
              }
              throw error;
            });
        })
        .push(function (Editor_bin) {
          if (Editor_bin) {
            return zip.getAttachment('/', '/');
          }
          return new Blob();
        })
        .push(function (zip_blob) {
          return jIO.util.readBlobAsDataURL(zip_blob);
        })
        .push(function (evt) {
          var data = {};
          data[g.props.key] = evt.target.result;
          // TODO it should be run on state change
          // if fail send int:1
          // it clear modification state onlyoffice
          DesktopOfflineAppDocumentEndSave(0);
          return data;
        })
        .push(undefined, function (error) {
          display_error(g, error);
        });
    })
    .onStateChange(function (m_dict) {
      var g = this;
      if (m_dict.changed === true) {
        return g.notifyChange();
      }
    });
}(rJS, RSVP, require, jIO));
