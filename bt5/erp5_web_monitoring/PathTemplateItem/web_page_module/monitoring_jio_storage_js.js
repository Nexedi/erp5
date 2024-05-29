/*
 * Copyright 2016, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/*jslint nomen: true */
/*global jIO, RSVP, Rusha, console, Blob */

(function (jIO, RSVP, Rusha, Blob, console) {
  "use strict";

  /**
   *
   * Sample OPML Tree Replicated Storage spec
   *
   * {
   *  "type": "replicatedopml",
   *  "remote_storage_unreachable_status": "WARNING",
   *  "remote_opml_check_time_interval": 86400000,
   *  "request_timeout": 0,
   *  local_sub_storage: {
   *    type: "query",
   *      sub_storage: {
   *        type: "indexeddb",
   *        database: "monitoring_local.db"
   *    }
   *  }
   * }
   *
   */

  var rusha = new Rusha(),
    OPML_ATTACHMENT_NAME = "__opml__",
    PROMISE_TYPE = "Promise",
    SOFTWARE_INSTANCE_TYPE = "Software Instance",
    INSTANCE_TREE_TYPE = "Instance Tree",
    OPML_PORTAL_TYPE = "Opml",
    ZONE_LIST = [
      "-1200",
      "-1100",
      "-1000",
      "-0900",
      "-0800",
      "-0700",
      "-0600",
      "-0500",
      "-0400",
      "-0300",
      "-0200",
      "-0100",
      "+0000",
      "+0100",
      "+0200",
      "+0300",
      "+0400",
      "+0500",
      "+0600",
      "+0700",
      "+0800",
      "+0900",
      "+1000",
      "+1100",
      "+1200"
    ];

  function generateHash(str) {
    return rusha.digestFromString(str);
  }

  function createStorage(context, storage_spec, key) {
    var signature;
    signature = generateHash(JSON.stringify(storage_spec));
    if (!context._remote_storage_dict.hasOwnProperty(key) ||
        signature !== context._remote_storage_dict[key].signature) {
      context._remote_storage_dict[key] = {
        storage: jIO.createJIO(storage_spec),
        signature: signature
      };
    }
    return context._remote_storage_dict[key].storage;
  }

  /**
   * The JIO OPML Tree Replicated Storage extension for monitor
   *
   * @class ReplicatedOPMLStorage
   * @constructor
   */
  function ReplicatedOPMLStorage(spec) {
    if (typeof spec.type !== 'string') {
      throw new TypeError(
        "ReplicatedOPMLStorage 'type' is not a string"
      );
    }
    if (spec.local_sub_storage === undefined) {
      throw new TypeError("ReplicatedOPMLStorage 'local_sub_storage' " +
                          "is not defined");
    }
    this._local_sub_storage = jIO.createJIO(spec.local_sub_storage);
    this._remote_storage_unreachable_status =
      spec.remote_storage_unreachable_status;
    this._remote_storage_dict = {};
    this._remote_parser_storage_type = spec.remote_parser_storage_type;
    if (this._remote_parser_storage_type === undefined) {
      this._remote_parser_storage_type = "parser";
    }
    this._remote_opml_check_time_interval =
      spec.remote_opml_check_time_interval;
    if (this._remote_opml_check_time_interval === undefined) {
      // one day in miliseconds
      this._remote_opml_check_time_interval = 86400000;
    }
    this._request_timeout = spec.request_timeout;
    if (this._request_timeout === undefined) {
      this._request_timeout = 0; // no timeout
    }
  }

  ReplicatedOPMLStorage.prototype.get = function () {
    return this._local_sub_storage.get.apply(this._local_sub_storage,
                                         arguments);
  };

  ReplicatedOPMLStorage.prototype.buildQuery = function () {
    return this._local_sub_storage.buildQuery.apply(this._local_sub_storage,
                                                arguments);
  };

  ReplicatedOPMLStorage.prototype.put = function (id, doc) {
    //allow app configuration types (forms, views, actions, etc)
    /*if (!doc.hasOwnProperty('portal_type') || doc.portal_type !== 'opml') {
      throw new TypeError("Cannot put object which portal_type is not 'opml'");
    }*/
    if (doc.active === undefined) {
      doc.active = true;
    }
    return this._local_sub_storage.put(id, doc);
  };

  ReplicatedOPMLStorage.prototype.hasCapacity = function (capacity) {
    if (capacity === 'include') {
      return true;
    }
    return this._local_sub_storage.hasCapacity.apply(this._local_sub_storage,
                                                     arguments);
  };

  ReplicatedOPMLStorage.prototype.getAttachment = function () {
    return this._local_sub_storage.getAttachment.apply(this._local_sub_storage,
                                                   arguments);
  };

  ReplicatedOPMLStorage.prototype.remove = function (id) {
    var storage = this._local_sub_storage;
    return storage.get(id)
      .push(function (doc) {
        if (doc.portal_type !== OPML_PORTAL_TYPE) {
          return storage.remove(id);
        }
        function removeOPMLTree(url) {
          var remove_id_list = [],
            remove_signature_id_list = [];

          // remove related instance tree
          remove_id_list.push(generateHash(id));
          // removed saved opml content
          remove_signature_id_list.push({
            id: url,
            name: url
          });
          // remove all related documents
          return storage.allDocs({
            select_list: ["xmlUrl", "url"],
            query: '(portal_type:"Opml Outline") AND (parent_url:"' + url + '")'
          })
            .push(function (document_result) {
              var i,
                query_list = [];

              for (i = 0; i < document_result.data.total_rows; i += 1) {
                query_list.push('(parent_id:"' +
                  document_result.data.rows[i].id + '")');

                remove_id_list.push(document_result.data.rows[i].id);
                remove_signature_id_list.push({
                  id: document_result.data.rows[i].id,
                  name: document_result.data.rows[i].value.xmlUrl
                });
                remove_signature_id_list.push({
                  id: document_result.data.rows[i].id,
                  name: document_result.data.rows[i].value.url
                });
              }
              // cleanup all sub opml items
              if (query_list.length > 0) {
                return storage.allDocs({query: query_list.join(" OR ")});
              }
              return {data: {total_rows: 0}};
            })
            .push(function (sub_item_result) {
              var j,
                i,
                k,
                remove_queue = new RSVP.Queue();

              function removeItem(key) {
                remove_queue
                  .push(function () {
                    return storage.remove(key);
                  });
              }
              function removeAttachmentItem(id, name) {
                remove_queue
                  .push(function () {
                    return storage.removeAttachment(id, name);
                  })
                  .push(undefined, function (error) {
                    if ((error instanceof jIO.util.jIOError) &&
                        (error.status_code === 404)) {
                      return undefined;
                    }
                    throw error;
                  });
              }

              // remove signatures
              for (k = 0; k < remove_signature_id_list.length; k += 1) {
                removeAttachmentItem(
                  remove_signature_id_list[k].id,
                  remove_signature_id_list[k].name
                );
              }
              // remove opml-outline sub-items (rss)
              for (j = 0; j < sub_item_result.data.total_rows; j += 1) {
                removeItem(sub_item_result.data.rows[j].id);
              }
              // remove opml-outline
              for (i = 0; i < remove_id_list.length; i += 1) {
                removeItem(remove_id_list[i]);
              }
              return remove_queue;
            })
            .push(function () {
              return storage.remove(url);
            });
        }
        return removeOPMLTree(id);
      });
  };

  ReplicatedOPMLStorage.prototype.allAttachments = function () {
    return this._local_sub_storage.allAttachments.apply(this._local_sub_storage,
                                                    arguments);
  };

  function getStorageUrl(storage_spec) {
    var spec = storage_spec;
    while (spec !== undefined) {
      if (spec.url !== undefined) {
        return spec.url;
      }
      if (spec.document_id !== undefined) {
        return spec.document_id;
      }
      spec = spec.sub_storage;
    }
    throw new Error("No url found on sub storage: " +
                    JSON.stringify(storage_spec));
  }

  function getDocumentAsAttachment(context, attachment_id, name) {
    return context._local_sub_storage.getAttachment(attachment_id, name)
      .push(undefined, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          return undefined;
        }
        console.error(error);
      })
      .push(function (attachment) {
        if (attachment) {
          return jIO.util.readBlobAsText(attachment)
            .then(function (evt) {
              return JSON.parse(evt.target.result);
            });
        }
        return {};
      });
  }

  function fixGlobalInstanceDocument(instance) {
    // Fix some property as backed is old, to keep backward compatibility
    // XXX - this method should be removed when all backend will be upgraded
    if (instance._embedded !== undefined) {
      if (instance._embedded.instance !== undefined) {
        // set aggregate_reference to the computer reference and make it
        // searchable
        instance.aggregate_reference = instance._embedded.instance.computer;
      }
      if (instance._embedded.hasOwnProperty('promises')) {
        // remove useless information from the document
        delete instance._embedded.promises;
      }
    }
    if (instance.hasOwnProperty('hosting-title')) {
      // hosting-title should be specialise_title
      instance.specialise_title = instance['hosting-title'];
      delete instance['hosting-title'];
    }
    // set portal_type is not defined
    if (!instance.hasOwnProperty('portal_type')) {
      instance.portal_type = SOFTWARE_INSTANCE_TYPE;
    }
    return instance;
  }

  function updateSubStorageStatus(context, signature_dict, next_status) {
    var key,
      update_status_queue = new RSVP.Queue();

    function updateStatus(id) {
      update_status_queue
        .push(function () {
          return context._local_sub_storage.get(id);
        })
        .push(function (doc) {
          if (doc.portal_type === PROMISE_TYPE) {
            doc.category = next_status;
            return context._local_sub_storage.put(id, doc);
          }
          if (doc.status !== undefined) {
            doc.status = next_status;
            return context._local_sub_storage.put(id, doc);
          }
        });
    }

    for (key in signature_dict) {
      if (signature_dict.hasOwnProperty(key)) {
        if (signature_dict[key].status !== next_status) {
          updateStatus(key);
          signature_dict[key].status = next_status;
        }
      }
    }
    return update_status_queue
      .push(function () {
        return signature_dict;
      });
  }

  function loadSubStorage(context, storage_spec, parent_id, index, type) {
    var sub_storage,
      result_dict,
      storage_key,
      url;

    url = getStorageUrl(storage_spec);
    storage_key = generateHash(parent_id + url);
    sub_storage = createStorage(context, storage_spec, storage_key);

    result_dict = {
      parent_id: parent_id,
      type:  type || storage_spec.type,
      current_signature: {},
      result: {data: {total_rows: 0}},
      url: url,
      parent_index: index
    };
    return sub_storage.allDocs({include_docs: true})
      .push(undefined, function (error) {
        //throw error;
        console.error(error);
        return undefined;
      })
      .push(function (result) {
        if (result === undefined) {
          if (context._remote_storage_unreachable_status !== undefined) {
            // update status of local documents
            // and set unreachable status
            return getDocumentAsAttachment(context, parent_id, url)
              .push(function (signature_document) {
                return updateSubStorageStatus(
                  context,
                  signature_document,
                  context._remote_storage_unreachable_status
                );
              })
              .push(function (signature_dict) {
                return signature_dict;
              });
          }
          return {};
        }
        result_dict.result = result;
        return getDocumentAsAttachment(
          context,
          parent_id,
          url
        );
      })
      .push(function (signature_document) {
        result_dict.current_signature = signature_document;
        return result_dict;
      });
  }

  function updateInstanceTreeState(hosting, element) {
    var status = element.status.toUpperCase();

    if (hosting.instance_amount === 0) {
      hosting.status_date = fixDateTimezone(element.date);
    }
    if (hosting.status === "ERROR") {
      return;
    } else if (status === "ERROR") {
      hosting.status = status;
    } else if (status === "WARNING") {
      hosting.status = status;
    } if (status === "OK" && hosting.status !== status) {
      hosting.status = status;
    }
  }

  function fixDateTimezone(date_string) {
    // set default timezone offset to UTC
    // XXX should be removed later
    if (ZONE_LIST.indexOf(date_string.slice(-5)) === -1) {
      return date_string + "+0000";
    }
    return date_string;
  }

  function getOpmlTree(context, opml_url, opml_spec, basic_login, opml_title) {
    var opml_storage,
      opml_document_list = [],
      delete_key_list = [],
      attachment_document_list = [],
      opml_result_list,
      current_signature_dict = {},
      fetch_remote_opml = false,
      instance_tree,
      id;

    id = generateHash(opml_url);
    opml_storage = createStorage(context, opml_spec, id);

    // Instance Tree is build from OPML and it has status
    instance_tree = {
      title: opml_title || "",
      portal_type: INSTANCE_TREE_TYPE,
      opml_url: opml_url,
      status: "WARNING",
      instance_amount: 0,
      status_date: (new Date()).toUTCString() + "+0000"
    };
    return getDocumentAsAttachment(context, opml_url, OPML_ATTACHMENT_NAME)
      .push(function (opml_doc) {
        var current_time = new Date().getTime();
        if (opml_doc.expire_time !== undefined) {
          fetch_remote_opml = (opml_doc.expire_time - current_time) < 0;
        } else {
          fetch_remote_opml = true;
        }
        if (fetch_remote_opml) {
          return opml_storage.allDocs({include_docs: true})
            .push(undefined, function (error) {
              if ((error instanceof jIO.util.jIOError) &&
                  (error.status_code === 404)) {
                return {data: {total_rows: 0}};
              }
              //throw error;
              console.error(error);
              return {data: {total_rows: 0}};
            })
            .push(function (opml_result) {
              opml_result_list = opml_result;
              if (opml_result.data.total_rows > 0) {
                attachment_document_list.push({
                  id: opml_url,
                  name: OPML_ATTACHMENT_NAME,
                  doc: {
                    expire_time: new Date().getTime() +
                      context._remote_opml_check_time_interval,
                    data: opml_result
                  }
                });
                return getDocumentAsAttachment(
                  context,
                  id,
                  opml_url
                );
              }
              return {};
            })
            .push(function (signature_dict) {
              current_signature_dict = signature_dict;
            });
        }
        opml_result_list = opml_doc.data;
      })
      .push(function () {
        var i,
          item,
          signature,
          doc_signature_dict = {},
          skip_add = false,
          id_hash,
          result_list = [],
          header_dict = {};

        if (opml_result_list.data.total_rows > 0) {
          if (opml_result_list.data.rows[0].doc.title) {
            instance_tree.title = opml_result_list.data.rows[0]
              .doc.title;
          }
          if (fetch_remote_opml) {
            header_dict = {
              dateCreated: opml_result_list.data.rows[0].doc.dateCreated,
              dateModified: opml_result_list.data.rows[0].doc.dateModified,
              opml_title: opml_result_list.data.rows[0].doc.title
            };
          }
        }

        for (i = 1; i < opml_result_list.data.total_rows; i += 1) {
          item = opml_result_list.data.rows[i];
          if (item.doc.xmlUrl !== undefined) {
            id_hash = generateHash(id + item.id);
            result_list.push(loadSubStorage(
              context,
              {
                type: context._remote_parser_storage_type,
                document_id: item.doc.xmlUrl,
                attachment_id: 'enclosure',
                parser: 'rss',
                sub_storage: {
                  type: "http",
                  timeout: context._request_timeout
                }
              },
              id_hash,
              i,
              PROMISE_TYPE
            ));
            // Load private docs
            if (item.doc.url !== undefined) {
              result_list.push(loadSubStorage(
                context,
                {
                  type: 'webhttp',
                  url: item.doc.url.replace('jio_private', 'private'),
                  basic_login: basic_login,
                  timeout: context._request_timeout
                },
                id_hash,
                i
              ));
            }

            if (fetch_remote_opml) {
              // Append this document signature to the list
              signature = generateHash(JSON.stringify(item.doc));
              doc_signature_dict[id_hash] = {
                signature: signature
              };
              if (current_signature_dict.hasOwnProperty(id_hash)) {
                if (current_signature_dict[id_hash].signature === signature) {
                  // remote document was not modified, delete and skip add
                  delete current_signature_dict[id_hash];
                  skip_add = true;
                }
                delete current_signature_dict[id_hash];
              }
              Object.assign(item.doc, {
                portal_type: "Opml Outline",
                parent_id: id,
                parent_url: opml_url,
                reference: id_hash,
                active: true
              });
              Object.assign(item.doc, header_dict);
              if (!skip_add) {
                opml_document_list.push({
                  id: id_hash,
                  doc: item.doc
                });
              }
            }
          }
        }
        if (fetch_remote_opml && Object.keys(doc_signature_dict).length > 0) {
          attachment_document_list.push({
            id: opml_url,
            name: opml_url,
            doc: doc_signature_dict
          });
          delete_key_list.push.apply(delete_key_list,
                                     Object.keys(current_signature_dict));
        }
        return RSVP.all(result_list);
      })
      .push(function (result_list) {
        var i,
          j,
          start,
          extra_dict;

        function applyItemToTree(item, item_result, extra_dict) {
          var id_hash,
            element = item.doc,
            signature,
            item_id = item.guid || item.id,
            status = (element.status || element.category),
            item_signature_dict = {};

          if (element.type === 'global') {
            updateInstanceTreeState(instance_tree, element);
            instance_tree.instance_amount += 1;
            if (element.aggregate_reference === undefined) {
              // XXX - document need to be updated to keep compatibility
              element = fixGlobalInstanceDocument(element);
            }
            // XXX - fixing date timezone
            element.date = fixDateTimezone(element.date);
          }
          // XXX - fixing date timezone
          if (element.pubDate !== undefined) {
            element.pubDate = fixDateTimezone(element.pubDate);
          }

          id_hash = generateHash(item_result.parent_id +
                                 item_result.url + item_id);

          if (extra_dict !== undefined) {
            Object.assign(element, extra_dict);
          }
          // Generating document signature
          signature = generateHash(JSON.stringify(element));
          item_signature_dict[id_hash] = {
            signature: signature,
            status: status
          };

          if (item_result.current_signature.hasOwnProperty(id_hash)) {
            if (item_result.current_signature[id_hash].signature ===
                signature) {
              // the document was not modified return
              delete item_result.current_signature[id_hash];
              return;
            }
            // the document exists and has changed
            delete item_result.current_signature[id_hash];
          }
          Object.assign(element, {
            parent_id: item_result.parent_id,
            portal_type: element.portal_type || element.type ||
              item_result.type,
            status: status,
            reference: element.reference || id_hash,
            active: true
          });
          opml_document_list.push({
            id: id_hash,
            doc: element
          });
          attachment_document_list.push({
            id: item_result.parent_id,
            name: item_result.url,
            doc: item_signature_dict
          });
        }

        for (i = 0; i < result_list.length; i += 1) {
          extra_dict = undefined;
          start = 0;
          if (result_list[i].result.data.total_rows > 0) {
            if (result_list[i].type === PROMISE_TYPE) {
              // the first element of rss is the header
              extra_dict = {
                lastBuildDate: fixDateTimezone(result_list[i].result.data.
                  rows[0].doc.lastBuildDate),
                channel: result_list[i].result.data.rows[0].doc.description,
                channel_item: result_list[i].result.data.rows[0].doc.title
              };
              start = 1;
            }
            for (j = start; j < result_list[i].result.data.total_rows; j += 1) {
              applyItemToTree(
                result_list[i].result.data.rows[j],
                result_list[i],
                extra_dict
              );
            }
            delete_key_list.push.apply(
              delete_key_list,
              Object.keys(result_list[i].current_signature)
            );
          } else if (Object.keys(result_list[i].current_signature).length > 0) {
            // if the remote data is empty and current_signature is not empty,
            // push to storage in case the status was changed
            // this help for speed optimisation
            attachment_document_list.push({
              id: result_list[i].parent_id,
              name: result_list[i].url,
              doc: result_list[i].current_signature
            });
          }
          else if (context._remote_storage_unreachable_status !== undefined) {
            if (result_list[i].type === "webhttp") {
              // In case it was impossible to get software Instance
              // Add an empty Software Instance with unreachable status
              applyItemToTree(
                {
                  id: "monitor.global",
                  doc: {
                    portal_type: SOFTWARE_INSTANCE_TYPE,
                    status: context._remote_storage_unreachable_status,
                    title: opml_result_list.data.rows[result_list[i]
                      .parent_index].doc.title,
                    date: new Date().toUTCString() + "+0000",
                    specialise_title: opml_result_list.data.rows[result_list[i]
                      .parent_index].doc.opml_title
                  }
                },
                result_list[i],
                undefined
              );
            }
          }
        }
        opml_document_list.push({
          id: id,
          doc: instance_tree
        });
        return [opml_document_list, delete_key_list, attachment_document_list];
      });
  }

  function pushDocumentToStorage(context, document_list, delete_key_list,
      attachment_document_list) {
    var document_queue = new RSVP.Queue(),
      i;

    function pushDocument(id, element) {
      document_queue
        .push(function () {
          return context._local_sub_storage.put(id, element);
        });
    }

    for (i = 0; i < document_list.length; i += 1) {
      pushDocument(
        document_list[i].id,
        document_list[i].doc
      );
    }
    return document_queue
      .push(function () {
        var k,
          remove_queue = new RSVP.Queue();

        // remove all document which were not updated
        function removeDocument(key) {
          remove_queue
            .push(function () {
              return context._local_sub_storage.remove(key);
            })
            .push(undefined, function (error) {
              if ((error instanceof jIO.util.jIOError) &&
                  (error.status_code === 404)) {
                return {};
              }
              throw error;
            });
        }

        for (k = 0; k < delete_key_list.length; k += 1) {
          removeDocument(delete_key_list[k]);
        }
        return remove_queue;
      })
      .push(function () {
        var j,
          signature_queue = new RSVP.Queue();

        function pushAttachment(id, name, element) {
          signature_queue
            .push(function () {
              return context._local_sub_storage.putAttachment(
                id,
                name,
                new Blob([JSON.stringify(element)], {type : 'application/json'})
              );
            })
            .push(undefined, function (error) {
              console.error(error);
            });
        }
        for (j = 0; j < attachment_document_list.length; j += 1) {
          pushAttachment(
            attachment_document_list[j].id,
            attachment_document_list[j].name,
            attachment_document_list[j].doc
          );
        }
      });
  }

  function syncOpmlStorage(context) {
    return context._local_sub_storage.allDocs({
      query: '(portal_type:"' + OPML_PORTAL_TYPE + '") AND (active:true) AND (url:"https://%")',
      select_list: ["title", "url", "basic_login"]
    })
      .push(function (storage_result) {
        var i,
          opml_queue = new RSVP.Queue();

        function syncFullOpml(storage_spec) {
          opml_queue
            .push(function () {
              return getOpmlTree(
                context,
                storage_spec.url,
                {
                  type: context._remote_parser_storage_type,
                  document_id: storage_spec.url,
                  attachment_id: 'enclosure',
                  parser: 'opml',
                  sub_storage: {
                    type: "http",
                    timeout: context._request_timeout
                  }
                },
                storage_spec.basic_login,
                storage_spec.title
              );
            })
            .push(function (result_list) {
              return pushDocumentToStorage(
                context,
                result_list[0],
                result_list[1],
                result_list[2]
              );
            });
        }
        for (i = 0; i < storage_result.data.total_rows; i += 1) {
          syncFullOpml(storage_result.data.rows[i].value);
        }
        return opml_queue;
      });
  }

  ReplicatedOPMLStorage.prototype.repair = function () {
    var context = this,
      argument_list = arguments;

    return new RSVP.Queue()
      .push(function () {
        return context._local_sub_storage.repair.apply(
          context._local_sub_storage,
          argument_list
        );
      })
      .push(function () {
        return syncOpmlStorage(context);
      });
  };

  jIO.addStorage('replicatedopml', ReplicatedOPMLStorage);

}(jIO, RSVP, Rusha, Blob, console));
