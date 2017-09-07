/*global window, rJS, btoa, RSVP, $, XMLHttpRequest */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, $, btoa, XMLHttpRequest) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,

    opml_url_template = Handlebars.compile(
      templater.getElementById("template-opmlurl-list").innerHTML
    ),
    notify_msg_template = Handlebars.compile(
      templater.getElementById("template-message-error").innerHTML
    );

  function validateHttpUrl(value) {
    if (/\(?(?:(http|https):\/\/)(?:((?:[^\W\s]|\.|-|[:]{1})+)@{1})?((?:www.)?(?:[^\W\s]|\.|-)+[\.][^\W\s]{2,4}|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[[\dabcedf:]+\])(?::(\d*))?([\/]?[^\s\?]*[\/]{1})*(?:\/?([^\s\n\?\[\]\{\}\#]*(?:(?=\.)){1}|[^\s\n\?\[\]\{\}\.\#]*)?([\.]{1}[^\s\?\#]*)?)?(?:\?{1}([^\s\n\#\[\]]*))?([\#][^\s\n]*)?\)?/i.test(value)) {
      return true;
    }
    return false;
  }

  function formatDate(d) {
    function addZero(n) {
      return n < 10 ? '0' + n : '' + n;
    }

    return d.getFullYear() + "-" + addZero(d.getMonth()+1)
      + "-" + addZero(d.getDate()) + " " + addZero(d.getHours())
      + ":" + addZero(d.getMinutes()) + ":" + addZero(d.getSeconds());
  }

  function checkCredential(gadget, url, title, hash) {
    var ouput;
    // Verify if login and password are correct for this URL
    if (url === undefined) {
      return {status: 'OK'};
    }
    return testUrl(url, hash)
      .then(function(result) {
        return result;
      }, function(error) {
        var ko_msg = {
            status: 'KO',
            msg: error.msg + ' (' + url + ')',
            title: title
          };
        return ko_msg;
      });
  }

  function testOPmlUrl(gadget, url, title) {
    return testUrl(url)
      .push(function (result) {
        if (result.status !== "OK") {
          var text =  result.code + ": " + url + " [ " + title + " ] is not reachable!",
            message_content = notify_msg_template({
              text: text,
              status: "error"
            });
          gadget.element.querySelector('.msgtext-box')
            .innerHTML += message_content;
          return false;
        }
        return true;
      });
  }

  function loadOPMLConfiguration(gadget) {
    return gadget.jio_allDocs({
      query: 'portal_type:"opml"',
      select_list: ['title', 'url', 'active', 'basic_login'],
      sort_on: [["title", "ascending"]]
    })
      .push(function (result) {
        var i,
          opml_list = [],
          cred_list,
          content;
        for (i = 0; i < result.data.total_rows; i += 1) {
          cred_list = atob(result.data.rows[i].value.basic_login).split(":");
          opml_list.push({
            key: result.data.rows[i].value.title + "#" +
              result.data.rows[i].value.url,
            href: "#page=settings_configurator&url=" +
              result.data.rows[i].value.url +
              '&tab=add&password=' + cred_list[1] +
              '&username=' + cred_list[0],
            link: result.data.rows[i].value.url,
            title: result.data.rows[i].value.title || '',
            status: (result.data.rows[i].value.active) ? "Enabled" : "Disabled"
          });
        }
        content = opml_url_template({opml_list: opml_list});
        gadget.element.querySelector(".opml-tablelinks > tbody")
          .innerHTML = content;
        return gadget.changeState({"opml_list": opml_list});
      });
  }

  function testUrl(url, credential_hash) {
    return new RSVP.Queue()
      .push(function () {
        return new RSVP.Promise(function (resolve, reject) {
          var xhr = new XMLHttpRequest();

          xhr.onload = function (event) {
            var response = event.target;
            if (response.status === 200) {
              resolve({status: 'OK'});
            } else {
              reject({
                status: 'ERROR',
                msg: new Error("XHR: " + response.status + ": " + response.statusText)
              });
            }
          };
    
          xhr.onerror = function (e) {
            reject({
              status: 'ERROR',
              msg: e.target.status + ": " + e.target.statusText
            });
          };
    
          xhr.open("GET", url, true);
          //xhr.withCredentials = true;
          if (credential_hash !== undefined) {
            xhr.setRequestHeader('Authorization', 'Basic ' + credential_hash);
          }
          xhr.send("");
        });
      });
  }

  function changeMonitorPassword(gadget, base_url, title, basic_login,
      password) {
    var url = base_url,
      jio_gadget,
      jio_options;

    url += (url.endsWith('/') ? '':'/') + 'config/';
    gadget.props.gindex += 1;
    return gadget.declareGadget("gadget_monitoring_jio.html",
        {
          element: gadget.element,
          scope: 'jio_' + gadget.props.gindex + "_gadget",
          sandbox: "public"
        }
      ).push(function(new_gadget) {
        jio_gadget = new_gadget;
        jio_gadget.createJio({
          type: "query",
          sub_storage: {
            type: "drivetojiomapping",
            sub_storage: {
              type: "dav",
              url: url,
              basic_login: basic_login
            }
          }
        });
        return jio_gadget.get('config');
      })
      .push(function (doc) {
        var i;
        if (doc) {
          for (i  = 0; i < doc.length; i += 1) {
            if (doc[i].key === 'monitor-password') {
              doc[i].value = password;
              return jio_gadget.put('config.tmp', doc);
            }
          }
        }
        return new Error("Cannot get document 'config.json' at : " % url);
      })
      .push(function () {
        return {status: 'OK'};
      }, function (error) {
        console.log(error);
        return {
          status: 'ERROR',
          code: error.target.status,
          url: base_url,
          title: title
        };
      });
    
  }

  gadget_klass
    /////////////////////////////
    // state
    /////////////////////////////
    .setState({
      deferred: "",
      sync_gadget: "",
      selected: "",
      jio_gadget: "",
      opml_list: ""
    })
    /////////////////////////////
    // ready
    /////////////////////////////
    .ready(function (gadget) {
      gadget.props = {gindex: 0};
      return new RSVP.Queue()
        .push(function () {
          return gadget.changeState({deferred: RSVP.defer()});
        })
        .push(function () {
          return gadget.getDeclaredGadget("sync_gadget")
            .push(function (sync_gadget) {
              return gadget.changeState({"sync_gadget": sync_gadget});
            });
        })
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget")
            .push(function (jio_gadget) {
              return gadget.changeState({"jio_gadget": jio_gadget});
            });
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_remove", "jio_remove")
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.updateHeader({
        title: "Configure monitoring OPML"/*,
        back_url: "#page=main",
        panel_action: false*/
      })
      .push(function () {
        return loadOPMLConfiguration(gadget);
      })
      .push(function () {
        var i;
        if (options.url !== undefined && options.url !== '') {
          gadget.element.querySelector("input[name='url']")
            .value = options.url;
          if (options.username !== undefined && options.username !== '' &&
              options.password !== undefined && options.password !== '') {
            //gadget.props.username = options.username;
            //gadget.props.password = options.password;
            gadget.element.querySelector("input[name='username']")
              .value = options.username;
            gadget.element.querySelector("input[name='password']")
              .value = options.password;
          }
        }
        return gadget.getSetting('latest_sync_time');
      })
      .push(function (latest_sync_time) {
        if (latest_sync_time !== undefined) {
          gadget.element.querySelector(".last-sync")
            .textContent = formatDate(new Date(latest_sync_time));
        } else {
          gadget.element.querySelector(".last-sync")
            .textContent = '--';
        }
      })
      .push(function () {
        if (!options.tab) {
          if (!options.url) {
            options.tab = 'manage';
          } else {
            options.tab = 'add';
          }
        }
        return gadget.changeState({"selected": options.tab});
      })
      .push(function () {
        return gadget.state.deferred.resolve();
      });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        sync_checkbox_list,
        alert_box,
        i;

      function setSyncTimerInterval(element) {
        var timer;
          if ($(element).prop('checked')) {
            timer = parseInt($(element).val(), 10);
            if (timer && !isNaN(timer)) {
              return new RSVP.Queue()
                .push(function () {
                  return gadget.setSetting('sync_data_interval', timer);
                });
            }
          }       
      }

      function setSelectSyncTime(time_interval) {
        var element_id = "#sync-data-";
        if (time_interval === 300000) {
          element_id += "5m";
        } else if (time_interval === 600000) {
          element_id += "10m";
        } else if (time_interval === 1200000) {
          element_id += "20m";
        } else if (time_interval === 1800000) {
          element_id += "30m";
        } else if (time_interval === 3600000) {
          element_id += "1h";
        }
        $(element_id).prop('checked', true);
        return $(gadget.element.querySelector(".sync-interval-controlgroup"))
          .controlgroup().controlgroup("refresh");
      }

      function getSelectedOPMLList() {
        var key_list = [],
          opml_selector = ".opml-tablelinks tr td input[type='checkbox']",
          check_list,
          i;
        check_list = gadget.element.querySelectorAll(opml_selector);
        if (!check_list) {
          return [];
        }
        for (i = 0; i < check_list.length; i += 1) {
          if ($(check_list[i]).prop('checked')) {
            key_list.push($(check_list[i]).prop('value'));
          }
        }
        return key_list;
      }

      function setFormValue(data) {
        if (data === undefined) {
          data = {};
        }
        gadget.element
          .querySelector("input[name='username']").value = data.username || "";
        gadget.element
          .querySelector("input[name='password']").value = data.password || "";
        gadget.element
          .querySelector("input[name='new_password']").value = data.new_password || "";
        gadget.element
          .querySelector("input[name='new_password_confirm']").value = data.new_password_confirm || "";
        gadget.element
          .querySelector("input[name='url']").value = data.url || "";
      }

      return new RSVP.Queue()
        .push(function () {
          return gadget.state.deferred.promise;
        })
        .push(function () {
          var item = "a[href='#config-" + gadget.state.selected + "']";
          alert_box = $(gadget.element
            .querySelector('.opml .alert-error'));
          return $(gadget.element.querySelector(item)).trigger('click');
        })
        .push(function () {
          return gadget.getSetting('sync_data_interval');
        })
        .push(function (time_interval) {
          return setSelectSyncTime(time_interval);
        })
        .push(function () {
          var promise_list = [];

          promise_list.push(loopEventListener(
            gadget.element.querySelector('.sync-all'),
            'click',
            true,
            function () {
              var title = gadget.element.querySelector('.sync-all span').textContent;
              return new RSVP.Queue()
                .push(function () {
                  gadget.element.querySelector('.sync-all span')
                    .textContent = 'Please wait...';
                  gadget.element.querySelector('.sync-all')
                    .disabled = true;
                  return gadget.state.sync_gadget.startSync({now: true});
                })
                .push(function () {
                  gadget.element.querySelector('.sync-all span')
                    .textContent = title;
                  gadget.element.querySelector('.sync-all')
                    .disabled = false;
                  return gadget.getSetting('latest_sync_time');
                })
                .push(function (latest_sync_time) {
                  if (latest_sync_time !== undefined) {
                    gadget.element.querySelector(".last-sync")
                      .textContent = formatDate(new Date(latest_sync_time));
                  } else {
                    gadget.element.querySelector(".last-sync")
                      .textContent = '--';
                  }
                });
            }
          ));

          promise_list.push(loopEventListener(
            gadget.element.querySelector("table th input[name='opml-all']"),
            'change',
            false,
            function (element) {
              if ($(element.target).prop('checked')) {
                return $(".opml-tablelinks tr td input[type='checkbox']").prop('checked', true);
              } else {
                return $(".opml-tablelinks tr td input[type='checkbox']").prop('checked', false);
              }
            }
          ));

          promise_list.push(
            $(gadget.element.querySelector(
              "input[name='configure-newpwd']"
            )).bind( "change", function(event, ui) {
              var confirm_pwd,
                new_pwd,
                box = gadget.element.querySelector(".opml .new-password");
              confirm_pwd = gadget.element.querySelector(
                ".opml input[name='new_password_confirm']"
              );
              new_pwd = gadget.element.querySelector(
                ".opml input[name='new_password']"
              );
              if ($(this).prop('checked')) {
                confirm_pwd.value = "";
                new_pwd.value = "";
                return $(box).slideDown();
              } else {
                confirm_pwd.value = "-";
                new_pwd.value = "-";
                return $(box).slideUp();
              }
            })
          );

          promise_list.push(loopEventListener(
            gadget.element.querySelector("a.opml-delete"),
            'click',
            true,
            function (element) {
              var key_list,
                promise_list = [],
                item_list,
                i;
              gadget.element.querySelector('.msgtext-box')
                .innerHTML = "";
              key_list = getSelectedOPMLList();
              if (key_list.length <= 0) {
                gadget.element.querySelector('.msgtext-box')
                  .innerHTML = notify_msg_template({
                    status: "info",
                    text: "No OPML selected!"
                  });
                return false;
              }
              for (i = 0; i < key_list.length; i += 1) {
                item_list = key_list[i].split("#");
                promise_list.push(gadget.jio_remove(
                  item_list.slice(1, item_list.length).join("#")
                ));
              }
              return new RSVP.Queue()
                .push(function () {
                  return RSVP.all(promise_list);
                })
                .push(undefined, function (error) {
                  console.log(error);
                  gadget.element.querySelector('.msgtext-box')
                    .innerHTML = notify_msg_template({
                      status: "error",
                      text: " ERROR while removing OPML(s)"
                    });
                  return;
                })
                .push(function () {
                  return gadget.reload();
                });
            }
          ));

          promise_list.push(loopEventListener(
            gadget.element.querySelector("a.opml-test"),
            'click',
            true,
            function (element) {
              var key_list,
                promise_list = [],
                item_list,
                title,
                i;
              gadget.element.querySelector('.msgtext-box')
                .textContent = "";
              key_list = getSelectedOPMLList();
              if (key_list.length <= 0) {
                gadget.element.querySelector('.msgtext-box')
                  .innerHTML = notify_msg_template({
                    status: "info",
                    text: "No OPML selected!"
                  });
                return false;
              }
              for (i = 0; i < key_list.length; i += 1) {
                item_list = key_list[i].split("#");
                title = item_list[0];
                promise_list.push(testOPmlUrl(
                  gadget,
                  item_list.slice(1, item_list.length).join("#"),
                  title
                ));
              }
              return new RSVP.Queue()
                .push(function () {
                  $(gadget.element.querySelector('.loadspinner'))
                    .removeClass('ui-content-hidden');
                  return RSVP.all(promise_list);
                })
                .push(function (result) {
                  var i,
                    state = true;
                  for (i = 0; i < result.length; i += 1) {
                    if (! result[i]) {
                      state = false;
                      break;
                    }
                  }
                  if (state) {
                    gadget.element.querySelector('.msgtext-box')
                      .innerHTML = notify_msg_template({
                        status: "ok",
                        text: "All OPML URLs was successfully tested."
                      });
                  }
                  $(gadget.element.querySelector('.loadspinner')).addClass('ui-content-hidden');
                });
            }
          ));

          promise_list.push(loopEventListener(
            gadget.element.querySelector("a.opml-state"),
            'click',
            true,
            function (element) {
              var key_list,
                promise_list = [],
                item_list,
                i;
              gadget.element.querySelector('.msgtext-box')
                .innerHTML = "";
              key_list = getSelectedOPMLList();
              if (key_list.length <= 0) {
                gadget.element.querySelector('.msgtext-box')
                  .innerHTML = notify_msg_template({
                    status: "info",
                    text: "No OPML selected!"
                  });
                return false;
              }
              for (i = 0; i < key_list.length; i += 1) {
                item_list = key_list[i].split("#");
                promise_list.push(gadget.jio_get(
                  item_list.slice(1, item_list.length).join("#")
                ));
              }
              return new RSVP.Queue()
                .push(function () {
                  return RSVP.all(promise_list);
                })
                .push(undefined, function (error) {
                  console.log(error);
                  gadget.element.querySelector('.msgtext-box')
                    .innerHTML = notify_msg_template({
                      status: "error",
                      text: "ERROR while updating OPML(s)"
                    });
                  return [];
                })
                .push(function (result_list) {
                  var i,
                    promise_state_list = [];
                  for (i = 0; i < result_list.length; i += 1) {
                    result_list[i].active = !result_list[i].active;
                    promise_state_list.push(gadget.jio_put(
                      result_list[i].url,
                      result_list[i]
                    ));
                  }
                  return RSVP.all(promise_state_list);
                })
                .push(function (result_list) {
                  if (result_list.length > 0) {
                    return loadOPMLConfiguration(gadget);
                  }
                });
            }
          ));

          promise_list.push(loopEventListener(
            gadget.element.querySelector('form.opml'),
            'submit',
            true,
            function () {
              var current_opml,
                username = '',
                password = '',
                opml_url = '',
                new_password = '',
                cnew_password = '',
                submit_text,
                button_submit = gadget.element
                  .querySelector('.opml button[type="submit"]');
              $(gadget.element.querySelector('.opml .alert-error'))
                .addClass('ui-content-hidden').text('');
              submit_text = button_submit.textContent;

              if ($(gadget.element.querySelector("input[name='configure-newpwd']")).prop('checked')) {
                new_password = gadget.element.querySelector("input[name='new_password']").value;
                cnew_password = gadget.element.querySelector("input[name='new_password_confirm']").value;
                if (new_password !== cnew_password) {
                  alert_box.removeClass('ui-content-hidden')
                    .text('The new password and it confirmation are differents!');
                  return false;
                }
              }

              function saveClick() {
                $(gadget.element.querySelector('.spinner'))
                            .removeClass('ui-content-hidden');
                button_submit.disabled = true; 
              }
              function endSave() {
                $(gadget.element.querySelector('.spinner'))
                            .addClass('ui-content-hidden');
                button_submit.disabled = false;
                button_submit.textContent = submit_text;
              }

              function pushNewOPML(opml_url, username, password, new_password) {
                var opml_dict = {
                    type: "opml",
                    portal_type: "opml",
                    url: opml_url,
                    basic_login: btoa(username + ':' + password),
                    active: true
                  },
                  update_password_list = [];

                function validateOPML() {
                  // read the opml to get the content and title
                  //delete gadget.state.jio_storage;
                  button_submit.textContent = "Reading OPML content...";
                  gadget.state.jio_gadget.createJio({
                    type: "query",
                    sub_storage: {
                      type: "parser",
                      document_id: opml_url,
                      attachment_id: 'enclosure',
                      parser: 'opml',
                      sub_storage: {
                        type: "http"
                      }
                    }
                  });
                  return gadget.state.jio_gadget.allDocs({
                    select_list: ['title', 'opml_title', 'xmlUrl', 'url']
                  })
                    .push(undefined, function (error) {
                      var msg = "";
                      if (error.currentTarget.responseType === "" ||
                          error.currentTarget.responseType === "text") {
                        msg = error.currentTarget.responseText;
                      }
                      alert_box.removeClass('ui-content-hidden')
                        .text(error.currentTarget.status +
                              ": Failed to access OPML URL. " + msg);
                      return {data: {total_rows: 0}};
                    })
                    .push(function (opml_result) {
                      var i,
                        check_list = [true];
                      if (opml_result.data.total_rows > 0) {
                        opml_dict.title = opml_result.data.rows[0].value.title;
                        for (i = 1; i < opml_result.data.total_rows; i += 1) {
                          if (opml_result.data.rows[i].value.url !== undefined) {
                            check_list.push(checkCredential(
                              gadget,
                              opml_result.data.rows[i].value.url,
                              opml_result.data.rows[i].value.title,
                              opml_dict.basic_login
                            ));
                            update_password_list.push({
                              base_url: opml_result.data.rows[i].value.url,
                              title: opml_result.data.rows[i].value.title
                            });
                          }
                        }
                        button_submit.textContent = "Validating password(s)...";
                        return RSVP.all(check_list);
                      }
                      return [false];
                    })
                    .push(function (status_list) {
                      var i,
                        error_msg = '';
                      for (i = 1; i < status_list.length; i += 1) {
                        if (status_list[i].status !== 'OK') {
                          error_msg += 'Login/password invalid for instance: ' +
                            status_list[i].title + '. ' +
                            status_list[i].msg + '\n';
                        }
                      }
                      if (error_msg !== '') {
                        alert_box.removeClass('ui-content-hidden')
                          .text(error_msg);
                        return false;
                      }
                      return status_list[0];
                    })
                    .push(function (previous_status) {
                      var i,
                        update_promise_list = [];
                      if (new_password === "") {
                        return previous_status;
                      }
                      if (!previous_status) {
                        return false;
                      }
                      button_submit.textContent = "Changing password(s)...";
                      for (i = 0; i < update_password_list.length; i += 1) {
                        update_promise_list.push(changeMonitorPassword(
                          gadget,
                          update_password_list[i].base_url,
                          update_password_list[i].title,
                          opml_dict.basic_login,
                          new_password
                        ));
                      }
                      return new RSVP.Queue()
                        .push(function () {
                          return RSVP.all(update_promise_list);
                        })
                        .push(function(result_list) {
                          var i,
                            error_msg = "";
                          for (i = 0; i < result_list.length; i += 1) {
                            if (result_list[i].status === 'ERROR') {
                              error_msg += 'ERROR ' + result_list[i].code +
                                '. [' + result_list[i].title + '] Failed to ' +
                                'change password, please try again\n';
                            }
                          }
                          if (error_msg !== "") {
                            alert_box.removeClass('ui-content-hidden')
                              .text(error_msg);
                            return false;
                          } else {
                            opml_dict.basic_login =
                              btoa(username + ':' + new_password);
                            return true;
                          }
                        });
                    });
                }

                saveClick();
                return gadget.jio_get(opml_dict.url)
                  .push(function (jio_doc) {
                    return jio_doc;
                  }, function (error) {
                    return {};
                  })
                  .push(function (doc) {
                    current_opml = doc;
                    return validateOPML();
                  })
                  .push(function (status) {
                    if (status) {
                      button_submit.textContent = "Saving OPML...";
                      return gadget.jio_put(opml_dict.url, opml_dict)
                        .push(function () {
                          endSave();
                          return gadget.redirect({
                            page: 'status_list'
                          });
                        });
                    }
                    endSave();
                  });
              }

              return new RSVP.Queue()
                .push(function () {
                  var promise_list = [],
                    i;
                  username = gadget.element
                    .querySelector("input[name='username']").value;
                  password = gadget.element
                    .querySelector("input[name='password']").value;
                  opml_url = gadget.element
                    .querySelector("input[name='url']").value;

                  if (!validateHttpUrl(opml_url)) {
                    alert_box.removeClass('ui-content-hidden')
                      .text(
                        "'" + opml_url + "' is not a valid OPML URL"
                      );
                    return false;
                  }
                  return pushNewOPML(opml_url, username, password,
                                     new_password);
                });
            }
          ));

          sync_checkbox_list = gadget.element.querySelectorAll("input[name='sync-data-timer']");
          for (i = 0; i < sync_checkbox_list.length; i += 1) {
            promise_list.push(
              $(sync_checkbox_list[i])
              .bind("change",
                setSyncTimerInterval.bind(gadget, sync_checkbox_list[i]))
            );
          }

          return RSVP.all(promise_list);
        });
    });

}(window, rJS, RSVP, $, btoa, XMLHttpRequest));

