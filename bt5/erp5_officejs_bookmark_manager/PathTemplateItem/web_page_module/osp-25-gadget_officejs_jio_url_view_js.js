/*globals window, rJS, Handlebars, RSVP, loopEventListener, console*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, Handlebars, loopEventListener) {
  "use strict";

  function saveContent(gadget, submit_event) {
    var i,
      doc = gadget.options.doc,
      now = new Date();
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          gadget.getSetting("portal_type"),
          gadget.getSetting("parent_relative_url")
        ]);
      })
      .push(function (answer_list) {
        doc.portal_type = answer_list[0];
        doc.parent_relative_url = answer_list[1];
        doc.modification_date = now.toISOString();

        for (i = 0; i < submit_event.target.length; i += 1) {
          // XXX Should check input type instead
          if (submit_event.target[i].name) {
            doc[submit_event.target[i].name] = submit_event.target[i].value;
          }
        }

        return gadget.put(gadget.options.jio_key, doc);
      });
  }

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
      .querySelector(".view-web-page-template")
      .innerHTML,
    template = Handlebars.compile(source);


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
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod("get", "jio_get")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("put", "jio_put")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("redirect", "redirect")

    .allowPublicAcquisition('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })

    .declareMethod('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      gadget.options.doc.title = gadget.options.doc.title || "";
      return new RSVP.Queue()
        .push(function () {
          return gadget.translateHtml(template(options.doc));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          return gadget.updateHeader({
            title: options.doc.title + " | Bookmark",
            save_action: true
          });
        })
        .push(function () {
          return gadget.props.deferred.resolve();
        });
    })

    /////////////////////////////////////////
    // Render text content gadget
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        text_gadget = null;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
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
          return loopEventListener(
            gadget.props.element.querySelector('form'),
            'submit',
            true,
            function (event) {
              return saveContent(gadget, event)
               .push(function () {
                  return gadget.redirect({page: "bookmark_list"});
                });
            }
          );
        });
    });

}(window, RSVP, rJS, Handlebars, loopEventListener));