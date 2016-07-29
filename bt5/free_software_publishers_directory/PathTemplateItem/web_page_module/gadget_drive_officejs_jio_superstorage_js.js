/*jslint indent: 2, maxerr: 3, nomen: true*/
/*global RSVP, Blob, jIO */

(function (jIO) {
  "use strict";

  /**
   * The jIO DavErp5Bridge extension
   *
   * @class DavErp5Bridge
   * @constructor
   */
  function DavErp5BridgeStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._sub_type = spec.sub_storage.type;
  }

  function addSlashes(s) {
    if (!s.startsWith('/')) {
      s = '/' + s;
    }
    if (!s.endsWith('/')) {
      s += '/';
    }
    return s;
  }

  function removeSlashes(s) {
    while (s.startsWith('/')) {
      s = s.substr(1);
    }
    while (s.endsWith('/')) {
      s = s.substring(0, s.length - 1);
    }
    return s;
  }

  function getResourceAndPosition(id) {
    var lastSlashIndex = id.lastIndexOf('/'), //XXX what if the resource name contains '/' ?
      position = id.substring(0, lastSlashIndex),
      resource = id.substring(lastSlashIndex + 1);
    return {position:  addSlashes(position),
            resource: resource};
  }

  DavErp5BridgeStorage.prototype.hasCapacity = function (capacity) {
    return (capacity === "list");
  };

  // called by allDocs method
  DavErp5BridgeStorage.prototype.buildQuery = function (options) {
    if (this._sub_type === 'dav') {
      return this._sub_storage.allAttachments(addSlashes(options.id))
        .push(function (all) {
          var dict = {},
            key;
          for (key in all) {
            if (all.hasOwnProperty(key)) {
              dict[key] = {'value': {'id': key, 'title': key} };
            }
          }
          return dict;
        });
    }
    if (this._sub_type === 'erp5') {
      return this._sub_storage.buildQuery({
        limit: [0, 100],
        select_list: ['id', 'title'],
        query: 'relative_url: "' + removeSlashes(options.id) + '/%"'
      });
    }
  };

  DavErp5BridgeStorage.prototype.getAttachment = function (id, name) {
    var substorage = this._sub_storage,
      data;
    if (name === 'enclosure') {
      if (this._sub_type === 'dav') {
        data = getResourceAndPosition(id);
        return substorage.getAttachment(data.position, data.resource);
      }
      if (this._sub_type === 'erp5') {
        id = removeSlashes(id);
        return substorage.getAttachment(id, 'links', {format: 'json'})
          .push(function (att) {
            return att._links.action_object_method;
          })
          .push(function (action_object_method) {
            if (action_object_method !== undefined) {
              return substorage.getAttachment(
                'erp5',
                action_object_method.href, // XXX action_object_method could be a list
                {
                  format: "blob"
                }
              )
                .push(function (attachmentContent) {
                  return attachmentContent;
                });
            }
            throw new jIO.util.jIOError("Cannot find 'action_object_method' link on this document.", 500);
          });
      }
    } else {
      throw new jIO.util.jIOError("Only support 'enclosure' attachment", 400);
    }
  };

  DavErp5BridgeStorage.prototype.putAttachment = function (id, name, text) {
    var substorage = this._sub_storage,
      data;
    if (name === 'enclosure') {
      if (this._sub_type === 'dav') {
        data = getResourceAndPosition(id);
        return substorage.putAttachment(data.position, data.resource, text);
      }
      if (this._sub_type === 'erp5') {
        data = new Blob([text], {"type" : "text/plain"});
        id = removeSlashes(id);
        return new RSVP.Queue()
          .push(function () {
            return jIO.util.readBlobAsDataURL(data);
          })
          .push(function (dataURI) {
            return substorage.put(id, {file: {url: dataURI.target.result}});
          });
      }
    }
    throw new jIO.util.jIOError("Only support 'enclosure' attachment", 400);
  };

  jIO.addStorage('daverp5mapping', DavErp5BridgeStorage);

}(jIO));