/*globals window, rJS, Handlebars, RSVP, location, indexedDB*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars,
  promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-setting-template")
                              .innerHTML,
    template = Handlebars.compile(source),
    update_check_flag = false;

  gadget_klass
    .ready(function (g) {
      g.props = {};
      g.options = null;
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("get", "jio_get")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getSetting('jid');
        })
        .push(function (login) {
          return gadget.translateHtml(template({jid: login}));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          return gadget.getSetting('language');
        })
        .push(function (language) {
          var element = gadget.props.element
            .querySelector("input[type=radio][value=" + language + "]");
          if (element) {
            element.setAttribute('checked', 'checked');
          }
          return gadget.updateHeader({
            title: "Setting"
          });
        })
        .push(function () {
          gadget.props.deferred.resolve();
        });
    })


    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this, login, passwd;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

          return promiseEventListener(
            gadget.props.element.querySelector('form.view-setting-form'),
            'submit',
            false
          );
        })
        .push(function () {
          gadget.props.element
            .querySelector("input[type=submit]").disabled = true;
          var checked_element = gadget.props.element
            .querySelector("input[type=radio]:checked"),
            language;
          if (checked_element !== null) {
            language = checked_element.value;
            if (language) {
              return gadget.setSetting('language', language);
            }
          }
          return;
        })
        .push(function () {
          login = gadget.props.element.querySelector("input[name=jid]").value;
          if (login) {
            return gadget.setSetting('jid', login);
          }
          return;
        })
        .push(function () {
          passwd = gadget.props.element
            .querySelector("input[name=passwd]").value;
          if (login && passwd) {
            var ac = window.btoa(login + ":" + passwd);
            return gadget.setSetting('_ac', ac);
          }
          return;
        })
        .push(function () {
          location.reload();
        });
    })


    //////////////////////////////
    // Reset Database
    //////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

          return loopEventListener(
            gadget.props.element
              .querySelector('input[type=button][name=reset_database]'),
            'click',
            false,
            function () {
                return new RSVP.Queue()
                  .push(function () {
                    indexedDB.deleteDatabase("jio:trade");
                    //alert('Deleted');
                  });
              }
          );
        });
    })


    //////////////////////////////
    // Update Application
    //////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {

          return loopEventListener(
            gadget.props.element
              .querySelector('input[type=button][name=update_application]'),
            'click',
            false,
            function () {
                return new RSVP.Queue()
                  .push(function () {
                  //alert(translateString('HTML5 App Update Started'));
                    update_check_flag = true;
                    if (window.applicationCache.status
                        === window.applicationCache.UNCACHED) {
                      location.reload();
                    } else if (window.applicationCache.status
                                 === window.applicationCache.IDLE) {
                      try {
                        window.applicationCache.update();
                      } catch (error) {
                        location.reload();
                      }
                    }
                  });
              }
          );
        });
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            window.applicationCache,
            'cached',
            false,
            function () {
              return new RSVP.Queue()
                .push(function () {
               // alert(translateString('HTML5 App Update Finished'));
                  location.reload();
                });
            }
          );
        });
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            window.applicationCache,
            'updateready',
            false,
            function(event){
              return new RSVP.Queue()
                .push(function () {
                //alert(translateString('HTML5 App Update Finished'));
                location.reload();
                });
            }
          );
        });
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            window.applicationCache,
            'error',
            false,
            function(event){
              return new RSVP.Queue()
                .push(function () {
                  window.applicationCache.update();
                });
            }
          );
        });
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return new RSVP.Queue()
            .push(function () {
              if(window.applicationCache.status == window.applicationCache.DOWNLOADING){
                alert(translateString('Downloading New Version Of HTML5 App'));
              }
            });
        })
        .push(function () {
          return loopEventListener(
            window.applicationCache,
            'downloading',
            false,
            function(event) {
              return new RSVP.Queue()
                .push(function () {
                //alert(translateString('Downloading New Version Of HTML5 App'));
                });
            }
          );
        });
    })
    .declareService(function(){
      var gadget = this;
      return new RSVP.Queue()
        .push(function(){
          return gadget.props.deferred.promise;
        })
        .push(function(){
          return loopEventListener(
            window.applicationCache,
            'progress',
            false,
            function(event){
              return new RSVP.Queue()
                .push(function(){
                  event.loaded / event.total;
                });
            }
          );
        });
    })
    .declareService(function(){
      var gadget = this;
      return new RSVP.Queue()
        .push(function(){
          return gadget.props.deferred.promise;
        })
        .push(function(){
          return loopEventListener(
            window.applicationCache,
            'noupdate',
            false,
            function(event){
              return new RSVP.Queue()
                .push(function(){
                if(update_check_flag === true){
                  alert(translateString('No HTML5 App Update Found'));
                  update_check_flag = false;
                }
                });
            }
          );
        });
    });


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
