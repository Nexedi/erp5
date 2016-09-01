/*jslint nomen: true, indent: 2, maxlen: 80*/
(function () {
  "use strict";

  /**
   * The jIO renderJS extension
   */

  function unserializeRjsResponse(storage, method_name, argument_list) {
    // console.info('--- rjs storage: ' + method_name);
    // console.log(Array.prototype.slice.call(argument_list));

    return new RSVP.Queue()
      .push(function () {
        return storage._created_promise;
      })
      .push(function () {
        return storage._gadget[method_name].apply(storage._gadget,
                                                  argument_list)
      })
      .push(function (result) {
        // console.log(result);
        result = JSON.parse(result);
        if (result.type === 'jio_response') {
          return result.result;
        } else if (result.type === 'jio_error') {
          throw new jIO.util.jIOError(result.message, result.status_code);
        } else {
          throw new Error(result);
        }
      }, function (error) {
        console.warn(error);
        throw error;
      });
  }

  function RenderJSStorage(spec) {
    this._gadget = spec.gadget;
    this._created_promise = this._gadget.createJio(spec.sub_storage);
  }

  RenderJSStorage.prototype.get = function () {
    return unserializeRjsResponse(this, 'get', arguments);
  };

  RenderJSStorage.prototype.post = function () {
    return unserializeRjsResponse(this, 'post', arguments);
  };

  RenderJSStorage.prototype.put = function () {
    return unserializeRjsResponse(this, 'put', arguments);
  };

  RenderJSStorage.prototype.remove = function () {
    return unserializeRjsResponse(this, 'remove', arguments);
  };

  RenderJSStorage.prototype.hasCapacity = function (name) {
    // console.info('--- rjs storage: hasCapacity ' + name);
    return ((name === 'list') || (name === 'query') || (name === 'limit') || (name === 'sort') || (name === 'select'));
  };

  RenderJSStorage.prototype.buildQuery = function () {
    return unserializeRjsResponse(this, 'buildQuery', arguments);
  };

  function dataURItoBlob(dataURI) {
    // convert base64 to raw binary data held in a string
    var byteString = atob(dataURI.split(',')[1]),
    // separate out the mime component
      mimeString = dataURI.split(',')[0].split(':')[1],
    // write the bytes of the string to an ArrayBuffer
      arrayBuffer = new ArrayBuffer(byteString.length),
      _ia = new Uint8Array(arrayBuffer),
      i;
    mimeString = mimeString.slice(0, mimeString.length - ";base64".length);
    for (i = 0; i < byteString.length; i += 1) {
      _ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([arrayBuffer], {type: mimeString});
  }

  RenderJSStorage.prototype.getAttachment = function (id, name, options) {
    var context = this;
    return new RSVP.Queue()
      .push(function () {
        return unserializeRjsResponse(context, 'getAttachment', [id, name, {format: 'data_url'}]);
      })
      .push(function (data_uri) {
        return dataURItoBlob(data_uri);
      });
  };

  RenderJSStorage.prototype.putAttachment = function (id, name, blob) {
    var context = this;
    if (blob.type !== 'application/json') {
      throw new Error('Only accept json blob, not ' + blob.type);
    }
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.readBlobAsText(blob);
      })
      .push(function (evt) {
        return unserializeRjsResponse(context, 'putAttachment', [id, name, evt.target.result]);
      });
  };

  RenderJSStorage.prototype.removeAttachment = function () {
    return unserializeRjsResponse(this, 'removeAttachment', arguments);
  };

  RenderJSStorage.prototype.allAttachments = function () {
    return unserializeRjsResponse(this, 'allAttachments', arguments);
  };

  jIO.addStorage('rjs', RenderJSStorage);
}());
