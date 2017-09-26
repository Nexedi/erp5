/*global jIO, RSVP, window, console */
/*jslint nomen: true, maxlen:160, indent:2*/
"use strict";

AscCommon.readBlobAsDataURL = function (blob) {
  var fr = new FileReader();
  return new RSVP.Promise(function (resolve, reject, notify) {
    fr.addEventListener("load", function () {
      resolve(fr.result);
    });
    fr.addEventListener("error", reject);
    fr.addEventListener("progress", notify);
    fr.readAsDataURL(blob);
  }, function () {
    fr.abort();
  });
};

AscCommon.downloadUrlAsBlob = function (url) {
  var xhr = new XMLHttpRequest();
  return new RSVP.Promise(function (resolve, reject) {
    xhr.open("GET", url);
    xhr.responseType = "blob";//force the HTTP response, response-type header to be blob
    xhr.onload = function () {
      if (this.status === 200) {
        resolve(xhr.response);
      } else {
        reject(this.status);
      }
    };
    xhr.onerror = reject;
    xhr.send();
  }, function () {
    xhr.abort();
  });
};

AscCommon.baseEditorsApi.prototype.jio_open = function () {
  var t = this,
    g = Common.Gateway;
  g.jio_getAttachment('/', 'body.txt')
    .push(undefined, function (error) {
      if (error.status_code === 404) {
        return g.props.value;
      }
      throw error;
    })
    .push(function (doc) {
      if (!doc) {
        switch (g.props.documentType) {
          case "presentation":
            doc = t.getEmpty();
            break;
          case "spreadsheet":
            doc = "XLSY;v2;2286;BAKAAgAAA+cHAAAEAwgAAADqCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGMFAAAAEQAAAAEMAAAABwEAAAAACAEAAAAABAoAAAAFAAAAAAUAAAAABnwAAAAHGgAAAAQGCgAAAEEAcgBpAGEAbAAGBQAAAAAAACRABxoAAAAEBgoAAABBAHIAaQBhAGwABgUAAAAAAAAkQAcaAAAABAYKAAAAQQByAGkAYQBsAAYFAAAAAAAAJEAHGgAAAAQGCgAAAEEAcgBpAGEAbAAGBQAAAAAAACRACB8AAAAJGgAAAAAGDgAAAEcARQBOAEUAUgBBAEwAAQSkAAAADhYDAAADPwAAAAABAQEBAQMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEpAAAAA0GGAAAAAABBAEEAAAAAAUBAAYEAAAAAAcBAAgBAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAEAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAgAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQCAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAQAAAAkEKwAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQpAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAEAAAAJBCwAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAQAAAAkEKgAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQJAAAAAkoAAAADRQAAAAABAAEBAAMBAAYEAAAAAAcEAAAAAAgEAAAAAAkEpAAAAAwEAAAAAA0GGAAAAAABBAEEAAAAAAUBAAYEAAAAAAcBAAgBAA8qAQAAECkAAAAABAAAAAAAAAABAQAAAAAEDAAAAE4AbwByAG0AYQBsAAUEAAAAAAAAABAnAAAAAAQAAAADAAAAAQEAAAAABAoAAABDAG8AbQBtAGEABQQAAAAPAAAAEC8AAAAABAAAAAYAAAABAQAAAAAEEgAAAEMAbwBtAG0AYQAgAFsAMABdAAUEAAAAEAAAABAtAAAAAAQAAAAEAAAAAQEAAAAABBAAAABDAHUAcgByAGUAbgBjAHkABQQAAAARAAAAEDUAAAAABAAAAAcAAAABAQAAAAAEGAAAAEMAdQByAHIAZQBuAGMAeQAgAFsAMABdAAUEAAAAEgAAABArAAAAAAQAAAAFAAAAAQEAAAAABA4AAABQAGUAcgBjAGUAbgB0AAUEAAAAEwAAABgAAAAAAwAAAAEBAAELAAAAAgYAAAAABAAAAADjAAAAAN4AAAABGwAAAAAGDAAAAFMAaABlAGUAdAAxAAEEAQAAAAIBAgIkAAAAAx8AAAABAQACBAEEAAADBAEAAAAEBAAAAAAFBXnalahdiStABAQAAABBADEAFhEAAAAXDAAAAAQBAAAAAQYBAAAAAQsKAAAAAQWamZmZmZkpQA48AAAAAAVxPQrXowA0QAEFKFyPwvUIOkACBXE9CtejADRAAwUoXI/C9Qg6QAQFcT0K16MANEAFBXE9CtejADRADwYAAAAAAQEBAQkQBgAAAAABAQEBAAkAAAAAGAYAAAACAQAAAAAAAAAA";
            break;
          case "text":
            doc = window.g_sEmpty_bin;
            break;
        }
      }
      t._OfflineAppDocumentEndLoad('', doc);
    })
    .push(undefined, function (error) {
      console.log(error);
    });
};

AscCommon.baseEditorsApi.prototype.jio_save = function () {
  var t = this,
    g = Common.Gateway,
    result = {},
    data = t.asc_nativeGetFile();
  if (g.props.save_defer) {
    // if we are run from getContent
    result[g.props.key] = data;
    g.props.save_defer.resolve(result);
    g.props.save_defer = null;
  } else {
    // TODO: rewrite to put_attachment
    return g.jio_putAttachment('/', 'body.txt', data)
      .push(undefined, function (error) {
        console.log(error);
      });
  }
};

AscCommon.loadSdk = function (sdkName, callback) {
  var config_file;

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

  if (window.AscNotLoadAllScript) {
    callback();
  } else {
    switch (sdkName) {
      case 'word':
        config_file = "webword.json";
        break;
      case 'cell':
        config_file = "webexcel.json";
        break;
      case 'slide':
        config_file = "webpowerpoint.json";
        break;
    }

    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: "GET",
          dataType: "json",
          url: "sdkjs/build/configs/" + config_file
        });
      })
      .push(function (response) {
        var queue = new RSVP.Queue(),
          sdk = response.target.response.compile.sdk;
        sdk.common.concat(sdk.private).forEach(function (url) {
          url = url.replace('../', './sdkjs/');
          queue.push(function () {
            return loadScript(url);
          });
        });
        return queue;
      })
      .push(callback);
  }
};