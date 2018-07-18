/*jslint nomen: true*/
/*global jIO, RSVP*/
(function (jIO, RSVP) {
  "use strict";

  function decodeJsonPointer(_str) {
    // https://tools.ietf.org/html/rfc6901#section-5
    return _str.replace(/~1/g, '/').replace(/~0/g, '~');
  }

  function encodeJsonPointer(_str) {
    // https://tools.ietf.org/html/rfc6901#section-5
    return _str.replace(/~/g, '~0').replace(/\//g, '~1');
  }

  /**
   * The jIO ZipToDocumentsBridgeStorage extension
   *
   * convert set of files provided zip container as
   * documents contains metadata for files
   * with attachment 'body' as file content
   *
   * @class ZipToDocumentsBridgeStorage
   * @constructor
   */
  function ZipToDocumentsBridgeStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    if (spec.generateMetadata) {
      this._generateMetadata = spec.generateMetadata;
    } else {
      throw new jIO.util.jIOError("Need specify generateMetadata function",
        400);
      /**
       * used for generate metadata for files
       * based on extension and file content.
       * used for determine supported or not
       * supported file by return undefined.
       *
       * @function generateMetadata
       */
      // example generateMetadata function
      // function generateMetadata(id, filename, path, body) {
      //   var ret;
      //   if (endsWith(filename, ".json")) {
      //     ret = {
      //       id: id,
      //       content_type: "application/json",
      //       reference: path
      //     };
      //     if (body) {
      //       if (body.$schema && body.$schema !== "") {
      //         ret.portal_type = "JSON Schema";
      //         ret.parent_relative_url = "schema_module";
      //         ret.title = body.title;
      //       } else {
      //         // XXX need schema relation property
      //         ret.portal_type = "JSON Document";
      //         ret.parent_relative_url = "document_module";
      //         ret.title = body.filename;
      //       }
      //     } else {
      //       ret.format = "json";
      //     }
      //     // used for detect supported extension
      //     return ret;
      //   }
      // }
    }
  }


  ZipToDocumentsBridgeStorage.prototype.get = function (id) {
    var context = this,
      path = "/" + decodeJsonPointer(id),
      idx = path.lastIndexOf('/') + 1,
      filename = path.substring(idx),
      dirname = path.substring(0, idx),
      file_supported;
    path = path.substring(1);
    file_supported = context._generateMetadata(id, filename, path);
    if (!file_supported) {
      return new RSVP.Queue()
        .push(function () {
          throw new jIO.util.jIOError("Cannot find document " + id,
            404);
        });
    }
    return context._sub_storage.getAttachment(dirname, filename,
                                              {format: file_supported.format}
      )
      .push(undefined, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          throw new jIO.util.jIOError("Cannot find document " + id,
            404);

        }
        throw error;
      })
      .push(function (attachment) {
        return context._generateMetadata(id, filename, path, attachment);
      });
  };

  ZipToDocumentsBridgeStorage.prototype.allAttachments = function (id) {
    var context = this,
      path = "/" + decodeJsonPointer(id),
      idx = path.lastIndexOf('/') + 1,
      filename = path.substring(idx),
      dirname = path.substring(0, idx);
    return context._sub_storage.getAttachment(dirname, filename)
      .push(function () {
        return {"data": {}};
      }, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          throw new jIO.util.jIOError("Cannot find document " + id,
            404);
        }
        throw error;
      });
  };

  ZipToDocumentsBridgeStorage.prototype.put = function (doc_id) {
    // we can not save file metadata(document in upper storage)
    // in zip so do nothing
    return RSVP.Queue()
      .push(function () {
        return doc_id;
      });
  };

  ZipToDocumentsBridgeStorage.prototype.remove = function (id) {
    var context = this,
      path = "/" + decodeJsonPointer(id),
      idx = path.lastIndexOf('/') + 1,
      filename = path.substring(idx),
      dirname = path.substring(0, idx);
    return context._sub_storage.removeAttachment(dirname, filename)
      .push(undefined, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          throw new jIO.util.jIOError("Cannot find document " + id,
            404);
        }
        throw error;
      });

  };

  ZipToDocumentsBridgeStorage.prototype.hasCapacity = function (capacity) {
    return ((capacity === "list") || (capacity === "include"));
  };

  ZipToDocumentsBridgeStorage.prototype.buildQuery = function (options) {
    var result_dict = {},
      context = this;
    return context._sub_storage.allDocs()
      .push(function (result) {
        var i,
          id,
          tasks = [];

        function push_doc(k, filename, path) {
          return function (json) {
            result_dict[k].doc = context._generateMetadata(k, filename, path, json);
          };
        }

        function f(dirname) {
          return function (dir) {
            var k,
              path,
              filename,
              attachment_tasks = [];

            for (filename in dir) {
              if (dir.hasOwnProperty(filename)) {
                path = dirname.substring(1) + filename;
                k = encodeJsonPointer(dirname.substring(1) + filename);
                // check file with extension supported
                if (context._generateMetadata(k, filename, path)) {
                  result_dict[k] = {
                    id: k,
                    value: {}
                  };
                  if (options.include_docs) {
                    attachment_tasks.push(
                      context._sub_storage.getAttachment(id, filename)
                        .push(push_doc(k, filename, path))
                    );
                  }
                }
              }
            }
            if (attachment_tasks.length > 0) {
              return RSVP.all(attachment_tasks);
            }
          };
        }

        for (i = 0; i < result.data.rows.length; i += 1) {
          id = result.data.rows[i].id;
          tasks.push(context._sub_storage.allAttachments(id)
                       .push(f(id)));
        }
        return RSVP.all(tasks);
      })
      .push(function () {
        var result = [],
          key;
        for (key in result_dict) {
          if (result_dict.hasOwnProperty(key)) {
            result.push(result_dict[key]);
          }
        }
        return result;
      });
  };

  ZipToDocumentsBridgeStorage.prototype.getAttachment = function (id,
                                                                  name,
                                                                  options) {
    if (name !== "data") {
      throw new jIO.util.jIOError("Only support 'data' attachment",
                                  400);
    }
    var path = "/" + decodeJsonPointer(id),
      idx = path.lastIndexOf('/') + 1,
      filename = path.substring(idx),
      dirname = path.substring(0, idx);

    return this._sub_storage.getAttachment(dirname, filename, options);
  };

  ZipToDocumentsBridgeStorage.prototype.putAttachment = function (id,
                                                                  name,
                                                                  blob) {
    if (name !== "data") {
      throw new jIO.util.jIOError("Only support 'data' attachment",
                                  400);
    }

    var path = "/" + decodeJsonPointer(id),
      idx = path.lastIndexOf('/') + 1,
      filename = path.substring(idx),
      dirname = path.substring(0, idx);
    return this._sub_storage.putAttachment(dirname, filename, blob);
  };

  ZipToDocumentsBridgeStorage.prototype.removeAttachment = function (id,
                                                                     name) {
    if (name !== "data") {
      throw new jIO.util.jIOError("Only support 'data' attachment" +
        " in document:" + id,
                                  400);
    }
    // document(metadata) with attachment === attachment in zip
    // so we can do nothing
  };

  ZipToDocumentsBridgeStorage.prototype.repair = function () {
    return this._sub_storage.repair.apply(this._sub_storage, arguments);
  };

  jIO.addStorage('ziptodocuments', ZipToDocumentsBridgeStorage);

}(jIO, RSVP));
