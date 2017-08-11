/*global window, rJS, RSVP, jsen, Rusha, $ */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, jsen, Rusha, $) {
  "use strict";

  function getMonitorSetting(gadget) {
    return gadget.jio_allDocs({
      select_list: ["basic_login", "url", "title", "active"],
      query: '(portal_type:"opml")'
    })
    .push(function (opml_result) {
      var i,
        opml_dict = {opml_description_list: []};
      for (i = 0; i < opml_result.data.total_rows; i+= 1) {
        opml_dict.opml_description_list.push(opml_result.data.rows[i].value);
      }
      return opml_dict;
    });
  }

  function validateJsonConfiguration(json_value, uses_old_schema) {
    var validate,
      json_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type" : "object",
        "properties": {
          "opml_description_list": {
            "description": "list of monitor opml URL",
            "type": "array",
            "required": ['basic_login', "url", "title"],
            "items": {
              "type": "object",
              "properties": {
                "url": {
                  "description": "OPML URL",
                  "type": "string"
                },
                "title": {
                  "description": "OPML title",
                  "type": "string"
                },
                "basic_login": {
                  "description": "credentials hash string",
                  "type": "string"
                },
                "active": {
                  "description": "OPML active state",
                  "type": "boolean",
                  "default": true
                }
              },
              "additionalProperties": false
            }
          }
        },
        "additionalProperties": false
      },
      old_json_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type" : "object",
        "properties": {
          "opml_description": {
            "description": "list of monitor opml URL",
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "href": {
                  "description": "OPML URL",
                  "type": "string"
                },
                "title": {
                  "description": "OPML title",
                  "type": "string"
                }
              },
              "additionalProperties": false
            }
          },
          "monitor_url": {
            "description": "list of registered monitor instance URL",
            "type": "array",
            "required": ['hash', "url", "parent_url"],
            "items": {
              "type": "object",
              "properties": {
                "hash": {
                  "description": "hash string",
                  "type": "string"
                },
                "login": {
                  "description": "login",
                  "type": "string",
                  "default": ""
                },
                "url": {
                  "description": "url of monitor instance",
                  "type": "string"
                },
                "parent_url": {
                  "description": "URL to parent instance",
                  "type": "string"
                }
              },
              "additionalProperties": false
            }
          }
        },
  
        "additionalProperties": false
      };

    return new RSVP.Queue()
      .push(function () {
        if (uses_old_schema !== undefined && uses_old_schema === true) {
          validate = jsen(old_json_schema);
        } else {
          validate = jsen(json_schema);
        }
        return validate(json_value);
      });
  }

  var gadget_klass = rJS(window),
    hashCode = new Rusha().digestFromString;

  gadget_klass
    .setState({deferred: ""})
    .ready(function (g) {
      return g.changeState({deferred: RSVP.defer()});
    })
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareMethod("render", function (options) {
      var gadget = this,
        url_description_dict;
      return gadget.updateHeader({
        title: "Monitoring OPML Import/Export"
      })
        .push(function () {
          return getMonitorSetting(gadget);
        })
        .push(function (setting_dict) {
          $(gadget.element.querySelector('textarea[name="settings-data"]'))
            .val(JSON.stringify(setting_dict));
          return gadget.state.deferred.resolve();
        });
    })


    .declareService(function () {
      var gadget = this,
        is_old_schema = false;

      return new RSVP.Queue()
        .push(function () {
          return gadget.state.deferred.promise;
        })
        .push(function () {
          return $(gadget.element.querySelector("a[href='#config-import']")).trigger('click');
        })
        .push(function () {
          var promise_list = [];
          promise_list.push(loopEventListener(
            gadget.element.querySelector('.btn-reload'),
            'click',
            true,
            function () {
              return new RSVP.Queue()
                .push(function () {
                  return getMonitorSetting(gadget);
                })
                .push(function (setting_dict) {
                  $(gadget.element.querySelector('textarea[name="settings-data"]'))
                    .val(JSON.stringify(setting_dict));
                });
            }
          ));

          promise_list.push(loopEventListener(
            gadget.element.querySelector('.btn-continue'),
            'click',
            true,
            function () {
              return gadget.redirect({
                  page: 'settings_configurator',
                  tab: 'manage'
                });
            }
          ));

          promise_list.push(loopEventListener(
            gadget.element.querySelector('.btn-save'),
            'click',
            true,
            function () {
              var json_string = $(gadget.element.querySelector('textarea[name="settings-data-input"]')).val(),
                configuration_dict,
                monitor_url_dict = {},
                monitor_opml_url_dict = {},
                error_msg = '',
                i;

              try {
                configuration_dict = JSON.parse(json_string);
              } catch (e) {
                return $(gadget.element.querySelector('.alert-error'))
                    .removeClass('ui-content-hidden')
                    .html('Error: Invalid json content!');
              }

              return validateJsonConfiguration(configuration_dict)
                .push(function (validate_result) {
                  if (!validate_result) {
                    // try validation on old setting format
                    is_old_schema = true;
                    return validateJsonConfiguration(configuration_dict, true);
                  }
                  return validate_result;
                })
                .push(function (validate_result) {
                  var settings_queue = new RSVP.Queue(),
                    not_imported = "",
                    item,
                    i,
                    j;

                  function pushSetting(id, config) {
                    settings_queue
                      .push(function () {
                        return gadget.jio_put(id, config);
                      })
                      .push(undefined, function (error) {
                        throw error;
                      });
                  }
                  if (validate_result) {
                    if (is_old_schema) {
                      //return settings_queue;
                      for (i = 0; i < configuration_dict.opml_description.length; i += 1) {
                        item = {
                          title: configuration_dict.opml_description[i].title,
                          url: configuration_dict.opml_description[i].href,
                          active: true,
                          portal_type: "opml"
                        };
                        for (j = 0; j < configuration_dict.monitor_url.length; j += 1) {
                          if (configuration_dict.monitor_url[j].parent_url ===
                              configuration_dict.opml_description[i].href) {
                            item.basic_login = configuration_dict.monitor_url[j].hash;
                            // XXX - all monitors password in opml should be the same
                            break;
                          }
                        }
                        if (item.basic_login !== undefined) {
                          pushSetting(item.url, item);
                        } else {
                          not_imported += "OPML [" + configuration_dict.opml_description[i].title +
                            "] was not imported, bad configuration...<br/>";
                        }
                      }
                    } else {
                      for (i = 0; i < configuration_dict.opml_description_list.length; i += 1) {
                        item = configuration_dict.opml_description_list[i];
                        item.portal_type = "opml";
                        pushSetting(item.url, item);
                      }
                    }
                    return settings_queue
                      .push(function () {
                        if (not_imported !== "") {
                          $(gadget.element.querySelector('.alert-error'))
                            .removeClass('ui-content-hidden')
                            .html(not_imported);
                          return false;
                        }
                        return true;
                      });
                  } else {
                    $(gadget.element.querySelector('.alert-error'))
                      .removeClass('ui-content-hidden')
                      .html('Error: Content is not a valid Monitoring Json configuration!');
                    return false;
                  }
                })
                .push(function (status) {
                  if (status) {
                    return gadget.redirect({
                      page: 'status_list'
                    });
                  }
                });
            }
          ));
        });
    });

}(window, rJS, RSVP, jsen, Rusha, $));