/*global RSVP, Blob*/
/*jslint nomen: true*/
(function (jIO, RSVP, Blob) {
  "use strict";

  function HttpStorage(spec) {
    if (spec.hasOwnProperty('catch_error')) {
      this._catch_error = spec.catch_error;
    } else {
      this._catch_error = false;
    }
  }

  HttpStorage.prototype.get = function (id) {
    var context = this;
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: 'HEAD',
          url: id
        });
      })
      .push(undefined, function (error) {
        if (context._catch_error) {
          return error;
        }
        if ((error.target !== undefined) &&
            (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find url " + id, 404);
        }
        throw error;
      })
      .push(function (response) {

        var key_list = ["Content-Disposition", "Content-Type", "Date",
                        "Last-Modified", "Vary", "Cache-Control", "Etag",
                        "Accept-Ranges", "Content-Range"],
          i,
          key,
          value,
          result = {};
        result.Status = response.target.status;
        for (i = 0; i < key_list.length; i += 1) {
          key = key_list[i];
          value = response.target.getResponseHeader(key);
          if (value !== null) {
            result[key] = value;
          }
        }
        return result;
      });
  };

  HttpStorage.prototype.allAttachments = function () {
    return {enclosure: {}};
  };

  HttpStorage.prototype.getAttachment = function (id, name) {
    var context = this;
    if (name !== 'enclosure') {
      throw new jIO.util.jIOError("Forbidden attachment: "
                                  + id + " , " + name,
                                  400);
    }
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: 'GET',
          url: id,
          dataType: "blob"
        });
      })
      .push(undefined, function (error) {
        if (context._catch_error) {
          return error;
        }
        if ((error.target !== undefined) &&
            (error.target.status === 404)) {
          throw new jIO.util.jIOError("Cannot find url " + id, 404);
        }
        throw error;
      })
      .push(function (response) {
        return new Blob(
          [response.target.response || response.target.responseText],
          {"type": response.target.getResponseHeader('Content-Type') ||
                   "application/octet-stream"}
        );
      });
  };

  jIO.addStorage('http', HttpStorage);

}(jIO, RSVP, Blob));