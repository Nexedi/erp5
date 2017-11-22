/*global window, rJS, RSVP, jsen, Handlebars, atob, btoa, DOMParser,
  URLSearchParams */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, jsen, Handlebars, atob, btoa, DOMParser,
           URLSearchParams) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    notify_msg_template = Handlebars.compile(
      templater.getElementById("template-message-error").innerHTML
    ),
    storage_selection = Handlebars.compile(
      templater.getElementById("storage-selection").innerHTML
    ),
    header_title = Handlebars.compile(
      templater.getElementById("template-section-title").innerHTML
    );

  function getMonitorSetting(gadget) {
    return gadget.jio_allDocs({
      select_list: ["basic_login", "url", "title", "active"],
      query: '(portal_type:"opml")'
    })
      .push(function (opml_result) {
        var i,
          opml_dict = {opml_description_list: []};
        for (i = 0; i < opml_result.data.total_rows; i += 1) {
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

  function importMonitorConfiguration(gadget, config) {
    var is_old_schema = false;
    gadget.state.message.textContent = "";
    return new RSVP.Queue()
      .push(function () {
        var configuration_dict;
        if (typeof config === 'string') {
          try {
            configuration_dict = JSON.parse(config);
          } catch (e) {
            gadget.state.message
              .innerHTML = notify_msg_template({
                status: 'error',
                message: 'Error: Invalid json content!'
              });
            return;
          }
        } else {
          configuration_dict = config;
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
              cred_list,
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
                      cred_list = atob(item.basic_login).split(':');
                      item.username = cred_list[0];
                      item.password = cred_list[1];
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
                  cred_list = atob(item.basic_login).split(':');
                  item.username = cred_list[0];
                  item.password = cred_list[1];
                  pushSetting(item.url, item);
                }
              }
              return settings_queue
                .push(function () {
                  if (not_imported !== "") {
                    gadget.state.message
                      .innerHTML = notify_msg_template({
                        status: 'error',
                        message: not_imported
                      });
                    return false;
                  }
                  return true;
                });
            }
            gadget.state.message
              .innerHTML = notify_msg_template({
                status: 'error',
                message: 'Error: Content is not a valid Monitoring Json configuration!'
              });
            return false;
          })
          .push(function (status) {
            if (status) {
              return gadget.redirect({
                "command": "display",
                "options": {"page": "settings_configurator"}
              });
            }
          });
      });
  }

  function readMonitoringParameter(parmeter_xml) {
    var parser = new DOMParser(),
      xmlDoc = parser.parseFromString(parmeter_xml, "text/xml"),
      parameter,
      uri_param,
      monitor_dict = {};

    parameter = xmlDoc.getElementById("monitor-setup-url");
    if (parameter !== undefined && parameter !== null) {
      // monitor-setup-url exists
      uri_param = new URLSearchParams(parameter.textContent);
      if (uri_param.has('url') && uri_param.has('password') &&
          uri_param.has('username') && uri_param.get('url').startsWith('http')) {
        return {
          opml_url: uri_param.get('url'),
          username: uri_param.get('username'),
          password: uri_param.get('password')
        };
      }
    } else {
      parameter = xmlDoc.getElementById("monitor-url");
      if (parameter !== undefined && parameter !== null) {
        monitor_dict.url = parameter.textContent.trim();
        parameter = xmlDoc.getElementById("monitor-user");
        if (parameter === undefined && parameter !== null) {
          return;
        }
        monitor_dict.username = parameter.textContent.trim();
        parameter = xmlDoc.getElementById("monitor-password");
        if (parameter === undefined && parameter !== null) {
          return;
        }
        monitor_dict.password = parameter.textContent.trim();
        return monitor_dict;
      }
    }
  }

  function getInstanceOPMLListFromMaster(gadget, limit) {
    var hosting_subscription_list = [],
      opml_list = [],
      uid_dict = {};
    if (limit === undefined) {
      limit = 100;
    }
    return gadget.state.erp5_gadget.allDocs({
      query: '(portal_type:"Hosting Subscription") AND (validation_state:"validated")',
      select_list: ['title', 'default_predecessor_uid', 'uid'],
      limit: [0, limit],
      sort_on: [
        ["creation_date", "descending"]
      ]
    })
      .push(function (result) {
        var i,
          uid_search_list = [];
        for (i = 0; i < result.data.total_rows; i += 1) {
          hosting_subscription_list.push({
            title: result.data.rows[i].value.title,
            relative_url: result.data.rows[i].id
          });
          uid_search_list.push(result.data.rows[i].value.uid);
          if (result.data.rows[i].value.default_predecessor_uid) {
            uid_dict[result.data.rows[i].value.default_predecessor_uid] = i;
          }
        }
        return gadget.state.erp5_gadget.allDocs({
          query: '(portal_type:"Software Instance") AND ' +
            '(predecessor_related_uid:("' + uid_search_list.join('","') + '"))',
          select_list: ['uid', 'predecessor_related_uid', 'connection_xml'],
          limit: [0, limit]
        });
      })
      .push(function (result) {
        var i,
          tmp_parameter,
          tmp_uid;

        for (i = 0; i < result.data.total_rows; i += 1) {
          tmp_uid = result.data.rows[i].value.uid;
          if (uid_dict.hasOwnProperty(tmp_uid)) {
            tmp_parameter = readMonitoringParameter(result.data.rows[i].value.connection_xml);
            if (tmp_parameter !== undefined) {
              opml_list.push({
                portal_type: "opml",
                title: hosting_subscription_list[uid_dict[tmp_uid]]
                  .title,
                relative_url: hosting_subscription_list[uid_dict[tmp_uid]]
                  .relative_url,
                url: tmp_parameter.opml_url,
                username: tmp_parameter.username,
                password: tmp_parameter.password,
                basic_login: btoa(tmp_parameter.username + ':' +
                                  tmp_parameter.password),
                active: true
              });
            }
          }
        }
        return opml_list;
      });
  }

  gadget_klass
    /////////////////////////////
    // state
    /////////////////////////////
    .setState({
      message: "",
      config: "",
      is_export: false,
      options: "",
      erp5_gadget: ""
    })
    .ready(function (g) {
      return g.getDeclaredGadget('erp5_gadget')
        .push(function (erp5_gadget) {
          return g.changeState({erp5_gadget: erp5_gadget});
        });
    })
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (form_doc) {
          return importMonitorConfiguration(gadget, form_doc.config);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        is_exporter = options.exporter === "true",
        message_element = gadget.element.querySelector('.ui-message-alert');
      message_element.textContent = "";
      if (options.url && !options.url.endsWith('/')) {
        options.url += '/';
      }
      if (is_exporter) {
        return new RSVP.Queue()
          .push(function () {
            return getMonitorSetting(gadget);
          })
          .push(function (configuration_dict) {
            return gadget.changeState({
              options: options,
              is_exporter: is_exporter,
              config: JSON.stringify(configuration_dict),
              message: message_element,
              sync: undefined
            });
          });
      }

      return gadget.changeState({
        options: options,
        is_exporter: is_exporter,
        config: "",
        message: message_element,
        sync: options.auto_sync,
        storage_url: options.url
      });
    })
    .onStateChange(function () {
      var gadget = this;
      if (gadget.state.options === "") {
        return;
      }
      return RSVP.Queue()
        .push(function () {
          var title_content;

          if (gadget.state.is_exporter) {
            title_content = header_title({
              title: "Export OPML Configurations",
              icon: "download"
            });
          } else {
            title_content = header_title({
              title: "Import OPML Configurations",
              icon: "upload"
            });
          }
          gadget.element.querySelector(".document-access h3").innerHTML = title_content;
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_view) {
          return form_view.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_config": {
                  "description": "Monitoring Settings Content (json format)",
                  "title": "Settings Content (JSON)",
                  "default": gadget.state.config || "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "config",
                  "hidden": 0,
                  "type": "TextAreaField"
                }
              }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "left",
                [["my_config"]]
              ]]
            }
          });
        })
        .push(function () {
          var new_options = JSON.parse(JSON.stringify(gadget.state.options));
          new_options.exporter = !gadget.state.is_exporter;
          new_options.auto_sync = undefined;
          new_options.url = undefined;
          return RSVP.all([
            gadget.getUrlFor({command: "display", options: new_options}),
            gadget.state.is_exporter
          ]);
        })
        .push(function (result) {
          var parameters = {
              page_title: "Monitoring Import-Export",
              export_url: result[1] ? undefined : result[0],
              import_url: result[1] ? result[0] : undefined
            };
          if (!result[1]) {
            parameters.submit_action = true;
            parameters.panel_action = false;
          }
          return gadget.updateHeader(parameters);
        })
        .push(function () {
          var div = gadget.element.querySelector('.storage-list');
          if (gadget.state.is_exporter) {
            while (div.firstChild) {
              div.removeChild(div.firstChild);
            }
            return;
          }
          return gadget.getUrlFor({command: "display", options: {page: "ojsm_erp5_configurator", type: "erp5"}})
            .push(function (url) {
              gadget.element.querySelector('.storage-list').innerHTML = storage_selection({
                documentlist: [{
                  "link": url,
                  "title": "SlapOS Master ERP5"
                }]
              });
            });
        })
        .push(function () {
          var has_failed = false;
          if (gadget.state.sync === "erp5" && gadget.state.storage_url) {
            // start import from erp5 now
            return gadget.notifySubmitting()
              .push(function () {
                return gadget.setSetting("hateoas_url", gadget.state.storage_url);
              })
              .push(function () {
                return gadget.state.erp5_gadget.createJio();
              })
              .push(function () {
                return gadget.getSetting('opml_import_limit', 100);
              })
              .push(function (select_limit) {
                return getInstanceOPMLListFromMaster(gadget, select_limit);
              })
              .push(undefined, function () {
                gadget.state.message
                  .innerHTML = notify_msg_template({
                    status: 'error',
                    message: 'Error: Failed to get Monitor Configuration from URL: ' +
                      gadget.state.storage_url
                  });
                has_failed = true;
                return [];
              })
              .push(function (opml_list) {
                var i,
                  push_queue = new RSVP.Queue();

                function pushOPML(opml_dict) {
                  push_queue
                    .push(function () {
                      return gadget.jio_put(opml_dict.url, opml_dict);
                    })
                    .push(undefined, function (error) {
                      throw error;
                    });
                }

                for (i = 0; i < opml_list.length; i += 1) {
                  pushOPML(opml_list[i]);
                }
                return push_queue;
              })
              .push(undefined, function () {
                gadget.state.message
                  .innerHTML = notify_msg_template({
                    status: 'error',
                    message: 'An error occurred while saving Configuration from URL: ' +
                      gadget.state.storage_url
                  });
                has_failed = true;
              })
              .push(function () {
                if (has_failed) {
                  return gadget.notifySubmitted({
                    message: "Failed to import Configurations",
                    status: "error"
                  });
                }
                return gadget.notifySubmitted({
                  message: "Configuration Saved!",
                  status: "success"
                });
              })
              .push(function () {
                if (!has_failed) {
                  return gadget.redirect({
                    "command": "display",
                    "options": {"page": "settings_configurator"}
                  });
                }
              });
          }
        });
    });
}(window, rJS, RSVP, jsen, Handlebars, atob, btoa, DOMParser, URLSearchParams));
