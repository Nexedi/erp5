/*global window, rJS, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  var gadget_klass = rJS(window);

  function getMessageList(gadget, limit) {

    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (jio_gadget) {
        return jio_gadget.get("logs");
      })
      .push(function (doc) {
        var error_list = [],
          key_list,
          size,
          i;
        if (doc === undefined) {
          doc = {};
        }
        key_list = Object.keys(doc).reverse();
        size = key_list.length;
        if (size < limit) {
          limit = size;
        }
        if (limit === undefined) {
          limit = 150;
        }
        for (i = 0; i < limit; i += 1) {
          error_list.push(doc[key_list[i]]);
        }
        return error_list;
      }, function (error) {
        if (error.status_code === 404) {
          return [];
        }
        throw error;
      });
  }

  function log(gadget, logs) {
    var jio_gadget;
    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (result) {
        jio_gadget = result;
        return jio_gadget.get("logs");
      })
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return {};
        }
        throw error;
      })
      .push(function (doc) {
        var value,
          d = new Date(),
          key = d.getTime(),
          key_list = Object.keys(doc),
          size = key_list.length;
        if (logs === undefined) {
          logs = {};
        }
        if (size >= 150) {
          // Reduce logs amount to not exceed the limit.
          delete doc[key_list[0]];
        }
        value = {
          date: d.toISOString().slice(0,10) + ' ' + d.getHours() + ':' + d.getMinutes() + ':' + d.getSeconds(),
          title: logs.title || '',
          message: logs.message.replace(/\n/g, '<br/>') || '',
          type: (logs.type || 'ERROR').toUpperCase(),
          method: logs.method || ''
        };
        doc[key] = value;
        return jio_gadget.put('logs', doc);
      });
  }

  gadget_klass
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getDeclaredGadget("jio_gadget")
      .push(function (jio_gadget) {
        return jio_gadget.createJio({
          type: "indexeddb",
          database: "setting"
        }, false);
      });
    })
    .declareMethod('log', function (logs) {
      var gadget = this;
      return log(gadget, logs);
    })
    .declareMethod('getMessageList', function (limit) {
      var gadget = this;
      return getMessageList(gadget, limit);
    })
    .declareService(function () {
      var gadget = this;


    });

}(window, rJS));