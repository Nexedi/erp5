/*globals window, rJS, Handlebars, RSVP*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, $) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-setting-template")
                              .innerHTML,
    template = Handlebars.compile(source);

  var update_check_flag = false;

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
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
        
        var login;
     new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('jid'),
          ]);
        })
        .push(function (setting_list) {
      
     login=setting_list; 
    });
       new RSVP.Queue()
        .push(function (result_list) {
        
    
          return gadget.translateHtml(template({jid:login}));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;

        var language;
     new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('language'),
          ]);
        })
        .push(function (setting_list) {
      
     language=setting_list; 
    });
        
        console.log(language);
        
          var element = gadget.props.element.querySelector("input[type=radio][value="+language+"]");
          if(element){
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
      var gadget = this;

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
        .push(function (submit_event) {
          gadget.props.element.querySelector("input[type=submit]").disabled = true;
          var checked_element = gadget.props.element.querySelector("input[type=radio]:checked");
          if (checked_element != null){
            var language = checked_element.value;
            if (language){
              //Cookies.set('language', language, {expires:36500});
              gadget.setSetting('language', language);
            }
          }
          var login = gadget.props.element.querySelector("input[name=jid]").value;
          var passwd = gadget.props.element.querySelector("input[name=passwd]").value;
          if(login){
           /* Cookies.remove('jid');
            Cookies.remove('jid', {path:''});
            Cookies.remove('jid', {path:'/'});
            Cookies.set('jid', login, {expires:36500, path:'/'})*/
            gadget.setSetting('jid', login);

          }
          if(login && passwd){
           /* Cookies.remove('__ac');
            Cookies.remove('__ac', {path:''});
            Cookies.remove('__ac', {path:'/'});
            Cookies.set('__ac', window.btoa(login + ":" + passwd), {expires:36500, path:'/'})*/
            gadget.setSetting('__ac', passwd);

          }
          location.reload();
        })
        .push(function () {
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
            gadget.props.element.querySelector('input[type=button][name=reset_database]'),
            'click',
            false,
            function (click_event) {
              return new RSVP.Queue()
                .push(function () {
                  indexedDB.deleteDatabase("jio:trade")
                  alert('Deleted');
                })
            }
          );
      })
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
            gadget.props.element.querySelector('input[type=button][name=update_application]'),
            'click',
            false,
            function (click_event) {
              return new RSVP.Queue()
                .push(function () {
                  alert(translateString('HTML5 App Update Started'));
                  update_check_flag = true;
                  if(window.applicationCache.status == window.applicationCache.UNCACHED){
                    location.reload();
                  }else if(window.applicationCache.status == window.applicationCache.IDLE){
                    try{
                      window.applicationCache.update();
                    }catch(error){
                      location.reload();
                    }
                  }
                })
            }
          );
        })
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
            'cached',
            false,
            function(event){
              return new RSVP.Queue()
                .push(function(){
                alert(translateString('HTML5 App Update Finished'));
                location.reload();
                })
            }
          );
        })
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
            'updateready',
            false,
            function(event){
              return new RSVP.Queue()
                .push(function(){
                alert(translateString('HTML5 App Update Finished'));
                location.reload();
                })
            }
          );
        })
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
            'error',
            false,
            function(event){
              return new RSVP.Queue()
                .push(function(){
                  window.applicationCache.update();
                })
            }
          );
        })
    })
    .declareService(function(){
      var gadget = this;
      return new RSVP.Queue()
        .push(function(){
          return gadget.props.deferred.promise;
        })
        .push(function(){
          return new RSVP.Queue()
            .push(function(){
              if(window.applicationCache.status == window.applicationCache.DOWNLOADING){
                alert(translateString('Downloading New Version Of HTML5 App'));
              }
            })
        })
        .push(function(){
          return loopEventListener(
            window.applicationCache,
            'downloading',
            false,
            function(event){
              return new RSVP.Queue()
                .push(function(){
                alert(translateString('Downloading New Version Of HTML5 App'));
                })
            }
          );
        })
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
                })
            }
          );
        })
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
                if(update_check_flag == true){
                  alert(translateString('No HTML5 App Update Found'));
                  update_check_flag = false;
                }
                })
            }
          );
        })
    })


}(window, document, RSVP, rJS, Handlebars, promiseEventListener, loopEventListener, jQuery));
