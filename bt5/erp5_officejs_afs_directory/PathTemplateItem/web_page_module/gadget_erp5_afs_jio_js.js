/*global window, rJS */
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, rJS) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////

  // XXX: the two methods below should be inside jiodev
  function mockupQueryParam(param, select_list) {
    var wild_param = param.replace(/[()]/g, "%").replace(/ /g, '');
    return ' (' + select_list.map(function (key) {
      return key + ':"' + wild_param + '"';
    }).join(' OR ') + ')';
  }

  function pimpQuery(option_dict) {
    var query_param_list = option_dict.query.split("AND"),
      query = option_dict.query,
      key_list = option_dict.select_list || [],
      param,
      len,
      i;

    for (i = 0, len = query_param_list.length; i < len; i += 1) {
      param = query_param_list[i];

      // search
      if (param.split(":").length !== 2) {
        return query.replace(param, mockupQueryParam(param, key_list));
      }

      // hide rows
      if (param.indexOf("catalog.uid") > 0) {
        return query.replace("catalog.", "");
      }
    }
    return query;
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (gadget) {

      // not so nice...
      return gadget.getDeclaredGadget('jio')
        .push(function (jio_gadget) {
          gadget.state_parameter_dict = {"jio_storage": jio_gadget};
        });
    })

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('redirect', 'redirect')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('createJio', function () {
      var gadget = this;

      gadget.state_parameter_dict.jio_storage.createJio({
        "type": "replicate",
        "check_local_modification": false,
        "check_local_creation": false,
        "check_local_deletion": false,
        "local_sub_storage": {
          "type": "query",
          "sub_storage": {type: "memory"}
        },
        "remote_sub_storage": {
          "type": "query",
          "sub_storage": {
            "type": "converter_storage",
            "sub_storage": {
              "type": "replicate",
              "check_local_modification": false,
              "check_local_creation": false,
              "check_local_deletion": false,
              "local_sub_storage": {
                "type": "query",
                "sub_storage": {type: "memory"}
              },
              "remote_sub_storage": {
                "type": "query",
                "sub_storage": {
                  type: "publisher_storage",
                  url: "/"
                }
              }
            }
          }
        }
      });
      return gadget.state_parameter_dict.jio_storage.repair();
    })

    .declareMethod('allDocs', function (option_dict) {
      if (option_dict && option_dict.query) {
        option_dict.query = pimpQuery(option_dict);
      }
      return this.state_parameter_dict.jio_storage.allDocs(option_dict);
    })
    .declareMethod('getAttachment', function (id, view) {
      return this.state_parameter_dict.jio_storage.getAttachment(id, view);
    })
    .declareMethod('get', function (id) {
      return this.state_parameter_dict.jio_storage.get(id);
    })
    .declareMethod('put', function (object1, object2) {
      return this.state_parameter_dict.jio_storage.put(object1, object2);
    })
    .declareMethod('repair', function () {
      return this.state_parameter_dict.jio_storage.repair();
    });

}(window, rJS));
