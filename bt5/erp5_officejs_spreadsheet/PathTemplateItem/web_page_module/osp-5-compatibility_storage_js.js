/*globals jIO, Blob, Rusha, RSVP, URI*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
(function (jIO, Blob, Rusha, RSVP, URI) {
  "use strict";

  var rusha = new Rusha(), stringify = jIO.util.stringify;

  function CompatibilityStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    var remote_storage = {
      type: "mapping",
      attachment_mapping_dict: {
        "data": {
          "get": {
            "uri_template": (new URI("hateoas"))
              .absoluteTo(spec.erp5_url)
              .toString() + "/{+id}/Document_downloadForOnlyOfficeApp"
          }
        }
      },
      sub_storage: {
        type: "erp5",
        url: (new URI("hateoas"))
              .absoluteTo(spec.erp5_url)
              .toString(),
        default_view_reference: "jio_view_attachment"
      }
    }, query = {
      query: 'portal_type:"' + spec.portal_type + '" ',
      sort_on: [["modification_date", "descending"]],
      limit: [0, 30]
    };
    this._signature_hash = "_replicate_" + rusha.digestFromString(
      stringify(spec) +
        stringify(remote_storage) +
        stringify(query)
    );
    this._signature_sub_storage = jIO.createJIO({
      type: "document",
      document_id: this._signature_hash,
      sub_storage: spec.sub_storage
    });
  }

  CompatibilityStorage.prototype.get = function () {
    return this._sub_storage.get.apply(this._sub_storage, arguments)
      .push(function (doc) {
        delete doc.data;
        return doc;
      });
  };

  CompatibilityStorage.prototype.put = function () {
    return this._sub_storage.put.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.post = function () {
    return this._sub_storage.post.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.remove = function () {
    return this._sub_storage.remove.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.hasCapacity = function () {
    return this._sub_storage.hasCapacity.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.repair = function () {
    var context = this;
    // Here fix the local storage for some cases.

    function checkSignature(doc) {
      if (doc.doc.data === undefined) {
        return context._sub_storage.getAttachment(doc.id, "data")
          .push(undefined, function (error) {
            if (error.status_code === 404) {
              return context._signature_storage.get(doc.id)
                .push(function (hash) {
                  delete hash.attachments_hash.data;
                  return context._signature_storage.put(doc.id, hash);
                })
                .push(undefined, function (error) {
                  if (error.status_code !== 404) {
                    throw error;
                  }
                  return;
                });
            }
            throw error;
          });
      }
    }

    return context._sub_storage.get(context._signature_hash)
      .push(function (signature) {
        if (!signature.is_repair) {
          return context._sub_storage.allDocs({include_doc: true})
            .push(function (doc_list) {
              var i, len = doc_list.length, promise_list = [];
              for (i = 0; i < len; i += 1) {
                promise_list.push(checkSignature(doc_list[i]));
              }
              return RSVP.all(promise_list);
            })
            .push(function () {
              return context._sub_storage.put(
                context._signature_hash,
                {is_repair: true}
              );
            });
        }
      })
      .push(undefined, function (error) {
        if (error.status_code !== 404) {
          throw error;
        }
        return;
      })
      .push(function () {
        return context._sub_storage.repair.apply(context._sub_storage, arguments);
      });
  };

  CompatibilityStorage.prototype.allAttachments = function (doc_id) {
    if (doc_id.indexOf("_replicate_") === 0) {
      return this._sub_storage.allAttachments.apply(
        this._sub_storage,
        arguments
      );
    }
    return this._sub_storage.getAttachment(doc_id, "data")
      .push(function (blob) {
        return [{"data": blob}];
      })
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return [];
        }
        throw error;
      });
  };

  CompatibilityStorage.prototype.getAttachment = function (doc_id) {
    var context = this;
    return context._sub_storage.getAttachment.apply(
      this._sub_storage,
      arguments
    )
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return context._sub_storage.get(doc_id)
            .push(function (doc) {
              var blob;
              if (doc.content_type === undefined ||
                  doc.content_type.indexOf("application/x-asc") === 0) {
                if (doc.data !== undefined) {
                  blob = new Blob([doc.data]);
                  return context.putAttachment(doc_id, "data", blob)
                    .push(function () {
                      return blob;
                    });
                }
              }
              throw new jIO.util.jIOError("no data", 404);
            });
        }
        throw error;
      });
  };

  CompatibilityStorage.prototype.putAttachment = function () {
    return this._sub_storage.putAttachment.apply(this._sub_storage, arguments);
  };

  CompatibilityStorage.prototype.removeAttachment = function () {
    return this._sub_storage.removeAttachment.apply(
      this._sub_storage,
      arguments
    );
  };

  CompatibilityStorage.prototype.buildQuery = function () {
    return this._sub_storage.buildQuery.apply(
      this._sub_storage,
      arguments
    )
      .push(function (result) {
        var i, len = result.length;
        for (i = 0; i < len; i += 1) {
          delete result[i].value.data;
          delete result[i].doc.data;
        }
        return result;
      });
  };

  jIO.addStorage('compatibility', CompatibilityStorage);

}(jIO, Blob, Rusha, RSVP, URI));