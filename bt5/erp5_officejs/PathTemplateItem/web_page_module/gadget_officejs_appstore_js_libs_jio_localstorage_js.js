/*
 * Copyright 2013, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, regexp: true */
/*global jIO, localStorage, setTimeout, complex_queries, window, define,
  exports, require */

/**
 * JIO Local Storage. Type = 'local'.
 * Local browser "database" storage.
 *
 * Storage Description:
 *
 *     {
 *       "type": "local",
 *       "mode": <string>,
 *         // - "localStorage" // default
 *         // - "memory"
 *       "username": <non empty string>, // to define user space
 *       "application_name": <string> // default 'untitled'
 *     }
 *
 * Document are stored in path
 * 'jio/localstorage/username/application_name/document_id' like this:
 *
 *     {
 *       "_id": "document_id",
 *       "_attachments": {
 *         "attachment_name": {
 *           "length": data_length,
 *           "digest": "md5-XXX",
 *           "content_type": "mime/type"
 *         },
 *         "attachment_name2": {..}, ...
 *       },
 *       "metadata_name": "metadata_value"
 *       "metadata_name2": ...
 *       ...
 *     }
 *
 * Only "_id" and "_attachments" are specific metadata keys, other one can be
 * added without loss.
 *
 * @class LocalStorage
 */

// define([module_name], [dependencies], module);
(function (dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  if (typeof exports === 'object') {
    return module(exports, require('jio'), require('complex_queries'));
  }
  window.local_storage = {};
  module(window.local_storage, jIO, complex_queries);
}([
  'exports',
  'jio',
  'complex_queries'
], function (exports, jIO, complex_queries) {
  "use strict";

  /**
   * Checks if an object has no enumerable keys
   *
   * @param  {Object} obj The object
   * @return {Boolean} true if empty, else false
   */
  function objectIsEmpty(obj) {
    var k;
    for (k in obj) {
      if (obj.hasOwnProperty(k)) {
        return false;
      }
    }
    return true;
  }

  var ram = {}, memorystorage, localstorage;

  /*
   * Wrapper for the localStorage used to simplify instion of any kind of
   * values
   */
  localstorage = {
    getItem: function (item) {
      var value = localStorage.getItem(item);
      return value === null ? null : JSON.parse(value);
    },
    setItem: function (item, value) {
      return localStorage.setItem(item, JSON.stringify(value));
    },
    removeItem: function (item) {
      return localStorage.removeItem(item);
    }
  };

  /*
   * Wrapper for the localStorage used to simplify instion of any kind of
   * values
   */
  memorystorage = {
    getItem: function (item) {
      var value = ram[item];
      return value === undefined ? null : JSON.parse(value);
    },
    setItem: function (item, value) {
      ram[item] = JSON.stringify(value);
    },
    removeItem: function (item) {
      delete ram[item];
    }
  };

  /**
   * The JIO LocalStorage extension
   *
   * @class LocalStorage
   * @constructor
   */
  function LocalStorage(spec) {
    if (typeof spec.username !== 'string' && !spec.username) {
      throw new TypeError("LocalStorage 'username' must be a string " +
                          "which contains more than one character.");
    }
    this._localpath = 'jio/localstorage/' + spec.username + '/' + (
      spec.application_name === null || spec.application_name ===
        undefined ? 'untitled' : spec.application_name.toString()
    );
    switch (spec.mode) {
    case "memory":
      this._database = ram;
      this._storage = memorystorage;
      this._mode = "memory";
      break;
    default:
      this._database = localStorage;
      this._storage = localstorage;
      this._mode = "localStorage";
      break;
    }
  }


  /**
   * Create a document in local storage.
   *
   * @method post
   * @param  {Object} command The JIO command
   * @param  {Object} metadata The metadata to store
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.post = function (command, metadata) {
    var doc, doc_id = metadata._id;
    if (!doc_id) {
      doc_id = jIO.util.generateUuid();
    }
    doc = this._storage.getItem(this._localpath + "/" + doc_id);
    if (doc === null) {
      // the document does not exist
      doc = jIO.util.deepClone(metadata);
      doc._id = doc_id;
      delete doc._attachments;
      this._storage.setItem(this._localpath + "/" + doc_id, doc);
      command.success({"id": doc_id});
    } else {
      // the document already exists
      command.error(
        "conflict",
        "document exists",
        "Cannot create a new document"
      );
    }
  };

  /**
   * Create or update a document in local storage.
   *
   * @method put
   * @param  {Object} command The JIO command
   * @param  {Object} metadata The metadata to store
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.put = function (command, metadata) {
    var doc, tmp, status;
    doc = this._storage.getItem(this._localpath + "/" + metadata._id);
    if (doc === null) {
      //  the document does not exist
      doc = jIO.util.deepClone(metadata);
      delete doc._attachments;
      status = "created";
    } else {
      // the document already exists
      tmp = jIO.util.deepClone(metadata);
      tmp._attachments = doc._attachments;
      doc = tmp;
      status = "no_content";
    }
    // write
    this._storage.setItem(this._localpath + "/" + metadata._id, doc);
    command.success(status);
  };

  /**
   * Add an attachment to a document
   *
   * @method putAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.putAttachment = function (command, param) {
    var that = this, doc, status = "ok";
    doc = this._storage.getItem(this._localpath + "/" + param._id);
    if (doc === null) {
      //  the document does not exist
      return command.error(
        "not_found",
        "missing",
        "Impossible to add attachment"
      );
    }

    // the document already exists
    // download data
    jIO.util.readBlobAsBinaryString(param._blob).then(function (e) {
      doc._attachments = doc._attachments || {};
      if (doc._attachments[param._attachment]) {
        status = "created";
      }
      doc._attachments[param._attachment] = {
        "content_type": param._blob.type,
        "digest": jIO.util.makeBinaryStringDigest(e.target.result),
        "length": param._blob.size
      };

      that._storage.setItem(that._localpath + "/" + param._id + "/" +
                            param._attachment, e.target.result);
      that._storage.setItem(that._localpath + "/" + param._id, doc);
      command.success(status,
                      {"digest": doc._attachments[param._attachment].digest});
    }, function (e) {
      command.error(
        "request_timeout",
        "blob error",
        "Error " + e.status + ", unable to get blob content"
      );
    }, function (e) {
      command.notify((e.loaded / e.total) * 100);
    });
  };

  /**
   * Get a document
   *
   * @method get
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.get = function (command, param) {
    var doc = this._storage.getItem(
      this._localpath + "/" + param._id
    );
    if (doc !== null) {
      command.success({"data": doc});
    } else {
      command.error(
        "not_found",
        "missing",
        "Cannot find document"
      );
    }
  };

  /**
   * Get an attachment
   *
   * @method getAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.getAttachment = function (command, param) {
    var doc;
    doc = this._storage.getItem(this._localpath + "/" + param._id);
    if (doc === null) {
      return command.error(
        "not_found",
        "missing document",
        "Cannot find document"
      );
    }

    if (typeof doc._attachments !== 'object' ||
        typeof doc._attachments[param._attachment] !== 'object') {
      return command.error(
        "not_found",
        "missing attachment",
        "Cannot find attachment"
      );
    }

    command.success({
      "data": this._storage.getItem(
        this._localpath + "/" + param._id +
          "/" + param._attachment
      ) || "",
      "content_type": doc._attachments[param._attachment].content_type || ""
    });
  };

  /**
   * Remove a document
   *
   * @method remove
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.remove = function (command, param) {
    var doc, i, attachment_list;
    doc = this._storage.getItem(this._localpath + "/" + param._id);
    attachment_list = [];
    if (doc !== null && typeof doc === "object") {
      if (typeof doc._attachments === "object") {
        // prepare list of attachments
        for (i in doc._attachments) {
          if (doc._attachments.hasOwnProperty(i)) {
            attachment_list.push(i);
          }
        }
      }
    } else {
      return command.error(
        "not_found",
        "missing",
        "Document not found"
      );
    }
    this._storage.removeItem(this._localpath + "/" + param._id);
    // delete all attachments
    for (i = 0; i < attachment_list.length; i += 1) {
      this._storage.removeItem(this._localpath + "/" + param._id +
                               "/" + attachment_list[i]);
    }
    command.success();
  };

  /**
   * Remove an attachment
   *
   * @method removeAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.removeAttachment = function (command, param) {
    var doc = this._storage.getItem(this._localpath + "/" + param._id);
    if (typeof doc !== 'object') {
      return command.error(
        "not_found",
        "missing document",
        "Document not found"
      );
    }
    if (typeof doc._attachments !== "object" ||
        typeof doc._attachments[param._attachment] !== "object") {
      return command.error(
        "not_found",
        "missing attachment",
        "Attachment not found"
      );
    }

    delete doc._attachments[param._attachment];
    if (objectIsEmpty(doc._attachments)) {
      delete doc._attachments;
    }
    this._storage.setItem(this._localpath + "/" + param._id, doc);
    this._storage.removeItem(this._localpath + "/" + param._id +
                             "/" + param._attachment);
    command.success();
  };

  /**
   * Get all filenames belonging to a user from the document index
   *
   * @method allDocs
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.allDocs = function (command, param, options) {
    var i, row, path_re, rows, document_list, document_object, delete_id;
    param.unused = true;
    rows = [];
    document_list = [];
    path_re = new RegExp(
      "^" + complex_queries.stringEscapeRegexpCharacters(this._localpath) +
        "/[^/]+$"
    );
    if (options.query === undefined && options.sort_on === undefined &&
        options.select_list === undefined &&
        options.include_docs === undefined) {
      rows = [];
      for (i in this._database) {
        if (this._database.hasOwnProperty(i)) {
          // filter non-documents
          if (path_re.test(i)) {
            row = { value: {} };
            row.id = i.split('/').slice(-1)[0];
            row.key = row.id;
            if (options.include_docs) {
              row.doc = JSON.parse(this._storage.getItem(i));
            }
            rows.push(row);
          }
        }
      }
      command.success({"data": {"rows": rows, "total_rows": rows.length}});
    } else {
      // create complex query object from returned results
      for (i in this._database) {
        if (this._database.hasOwnProperty(i)) {
          if (path_re.test(i)) {
            document_list.push(this._storage.getItem(i));
          }
        }
      }
      options.select_list = options.select_list || [];
      if (options.select_list.indexOf("_id") === -1) {
        options.select_list.push("_id");
        delete_id = true;
      }
      if (options.include_docs === true) {
        document_object = {};
        document_list.forEach(function (meta) {
          document_object[meta._id] = meta;
        });
      }
      complex_queries.QueryFactory.create(options.query || "").
        exec(document_list, options);
      document_list = document_list.map(function (value) {
        var o = {
          "id": value._id,
          "key": value._id
        };
        if (options.include_docs === true) {
          o.doc = document_object[value._id];
          delete document_object[value._id];
        }
        if (delete_id) {
          delete value._id;
        }
        o.value = value;
        return o;
      });
      command.success({"data": {
        "total_rows": document_list.length,
        "rows": document_list
      }});
    }
  };

  /**
   * Check the storage or a specific document
   *
   * @method check
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.check = function (command, param) {
    this.genericRepair(command, param, false);
  };

  /**
   * Repair the storage or a specific document
   *
   * @method repair
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.repair = function (command, param) {
    this.genericRepair(command, param, true);
  };

  /**
   * A generic method that manage check or repair command
   *
   * @method genericRepair
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Boolean} repair If true then repair else just check
   */
  LocalStorage.prototype.genericRepair = function (command, param, repair) {

    var that = this, result;

    function referenceAttachment(param, attachment) {
      if (jIO.util.indexOf(param.referenced_attachments, attachment) !== -1) {
        return;
      }
      var i = jIO.util.indexOf(param.unreferenced_attachments, attachment);
      if (i !== -1) {
        param.unreferenced_attachments.splice(i, 1);
      }
      param.referenced_attachments[param.referenced_attachments.length] =
        attachment;
    }

    function attachmentFound(param, attachment) {
      if (jIO.util.indexOf(param.referenced_attachments, attachment) !== -1) {
        return;
      }
      if (jIO.util.indexOf(param.unreferenced_attachments, attachment) !== -1) {
        return;
      }
      param.unreferenced_attachments[param.unreferenced_attachments.length] =
        attachment;
    }

    function repairOne(param, repair) {
      var i, doc, modified;
      doc = that._storage.getItem(that._localpath + "/" + param._id);
      if (doc === null) {
        return; // OK
      }

      // check document type
      if (typeof doc !== 'object') {
        // wrong document
        if (!repair) {
          return {"error": true, "answers": [
            "conflict",
            "corrupted",
            "Document is unrecoverable"
          ]};
        }
        // delete the document
        that._storage.removeItem(that._localpath + "/" + param._id);
        return; // OK
      }
      // good document type
      // repair json document
      if (!repair) {
        if (!(new jIO.Metadata(doc).check())) {
          return {"error": true, "answers": [
            "conflict",
            "corrupted",
            "Some metadata might be lost"
          ]};
        }
      } else {
        modified = jIO.util.uniqueJSONStringify(doc) !==
          jIO.util.uniqueJSONStringify(new jIO.Metadata(doc).format()._dict);
      }
      if (doc._attachments !== undefined) {
        if (typeof doc._attachments !== 'object') {
          if (!repair) {
            return {"error": true, "answers": [
              "conflict",
              "corrupted",
              "Attachments are unrecoverable"
            ]};
          }
          delete doc._attachments;
          that._storage.setItem(that._localpath + "/" + param._id, doc);
          return; // OK
        }
        for (i in doc._attachments) {
          if (doc._attachments.hasOwnProperty(i)) {
            // check attachment existence
            if (that._storage.getItem(that._localpath + "/" + param._id + "/" +
                                      i) !== 'string') {
              if (!repair) {
                return {"error": true, "answers": [
                  "conflict",
                  "missing attachment",
                  "Attachment \"" + i + "\" of \"" + param._id + "\" is missing"
                ]};
              }
              delete doc._attachments[i];
              if (objectIsEmpty(doc._attachments)) {
                delete doc._attachments;
              }
              modified = true;
            } else {
              // attachment exists
              // check attachment metadata
              // check length
              referenceAttachment(param, param._id + "/" + doc._attachments[i]);
              if (doc._attachments[i].length !== undefined &&
                  typeof doc._attachments[i].length !== 'number') {
                if (!repair) {
                  return {"error": true, "answers": [
                    "conflict",
                    "corrupted",
                    "Attachment metadata length corrupted"
                  ]};
                }
                // It could take a long time to get the length, no repair.
                // length can be omited
                delete doc._attachments[i].length;
              }
              // It could take a long time to regenerate the hash, no check.
              // Impossible to discover the attachment content type.
            }
          }
        }
      }
      if (modified) {
        that._storage.setItem(that._localpath + "/" + param._id, doc);
      }
      // OK
    }

    function repairAll(param, repair) {
      var i, result;
      for (i in that._database) {
        if (that._database.hasOwnProperty(i)) {
          // browsing every entry
          if (i.slice(0, that._localpath.length) === that._localpath) {
            // is part of the user space
            if (/^[^\/]+\/[^\/]+$/.test(i.slice(that._localpath.length + 1))) {
              // this is an attachment
              attachmentFound(param, i.slice(that._localpath.length + 1));
            } else if (/^[^\/]+$/.test(i.slice(that._localpath.length + 1))) {
              // this is a document
              param._id = i.slice(that._localpath.length + 1);
              result = repairOne(param, repair);
              if (result) {
                return result;
              }
            } else {
              // this is pollution
              that._storage.removeItem(i);
            }
          }
        }
      }
      // remove unreferenced attachments
      for (i = 0; i < param.unreferenced_attachments.length; i += 1) {
        that._storage.removeItem(that._localpath + "/" +
                                 param.unreferenced_attachments[i]);
      }
    }

    param.referenced_attachments = [];
    param.unreferenced_attachments = [];
    if (typeof param._id === 'string') {
      result = repairOne(param, repair) || {};
    } else {
      result = repairAll(param, repair) || {};
    }
    if (result.error) {
      return command.error.apply(command, result.answers || []);
    }
    command.success.apply(command, result.answers || []);
  };

  jIO.addStorage('local', LocalStorage);

  //////////////////////////////////////////////////////////////////////
  // Tools

  function createLocalDescription(username, application_name) {
    if (typeof username !== 'string') {
      throw new TypeError("LocalStorage username must be a string");
    }
    var description = {
      "type": "local",
      "username": username
    };
    if (typeof application_name === 'string') {
      description.application_name = application_name;
    }
    return description;
  }

  function createMemoryDescription(username, application_name) {
    var description = createLocalDescription(username, application_name);
    description.mode = "memory";
    return description;
  }

  /**
   * Tool to help users to create local storage description for JIO
   *
   * @param  {String} username The username
   * @param  {String} [application_name] The application_name
   * @param  {String} [mode="localStorage"] Use localStorage or memory
   * @return {Object} The storage description
   */
  function createDescription(username, application_name, mode) {
    if (mode === undefined || mode.toString() === 'localStorage') {
      return createLocalDescription(username, application_name);
    }
    if (mode.toString() === 'memory') {
      return createMemoryDescription(username, application_name);
    }
    throw new TypeError("Unknown LocalStorage '" + mode.toString() + "' mode");
  }

  exports.createDescription = createDescription;
  exports.createLocalDescription = createLocalDescription;
  exports.createMemoryDescription = createMemoryDescription;

  function clearLocalStorage() {
    var k;
    for (k in localStorage) {
      if (localStorage.hasOwnProperty(k)) {
        if (/^jio\/localstorage\//.test(k)) {
          localStorage.removeItem(k);
        }
      }
    }
  }

  function clearMemoryStorage() {
    jIO.util.dictClear(ram);
  }

  exports.clear = clearLocalStorage;
  exports.clearLocalStorage = clearLocalStorage;
  exports.clearMemoryStorage = clearMemoryStorage;

}));
