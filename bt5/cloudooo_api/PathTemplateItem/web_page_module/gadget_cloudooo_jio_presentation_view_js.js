/*globals window, rJS, Handlebars, RSVP, loopEventListener, console, document,
  jIO */
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, loopEventListener, jIO) {
  "use strict";

  function saveContent(gadget, submit_event) {
    var i,
      doc = gadget.options.doc,
      file;
    doc.modification_date = (new Date()).toISOString();
    for (i = 0; i < submit_event.target.length; i += 1) {
      // XXX Should check input type instead
      if (submit_event.target[i].name && submit_event.target[i].name !== "field_my_file") {
        doc[submit_event.target[i].name] = submit_event.target[i].value;
      } else if (submit_event.target[i].name ===  "field_my_file") {
        file = submit_event.target[i].files[0];
      }
    }
    return gadget.put(gadget.options.jio_key, doc)
      .push(function () {
        console.log(file);
        if (file !== undefined) {
          return gadget.jio_putAttachment(
            gadget.options.jio_key,
            "enclosure",
            file
            );
        }
        return true;//doc.data = data.text_content;
      });
  }

  function getMaxHeight(wrap_obj) {
    var height;
    if (wrap_obj) {
      height = window.innerHeight - wrap_obj.offsetTop;
    } else {
      height = window.innerHeight;
    }
    if (height < 400) {
      height = 400;
    }
    return height + "px";
  }

  function setFillStyle(gadget) {
    var iframe = gadget.props.element.querySelector('iframe'),
      height = getMaxHeight(iframe),
      width = "100%";
    iframe.setAttribute(
      'style',
      'width: ' + width + '; border: 0 none; height: ' + height
    );
    return {height: height, width: width};
  }

  function switchMaximizeMode(gadget) {
    var fullscreen_classname = "ui-content-fullscreen",
      wrap = gadget.props.element.querySelector('iframe'),
      info = gadget.props.fullScreenRestore;
    if (wrap.className.search(" " + fullscreen_classname) === -1) {
      gadget.props.fullScreenRestore = {
        scrollTop: window.pageYOffset,
        scrollLeft: window.pageXOffset,
        width: wrap.style.width,
        height: wrap.style.height
      };

      wrap.style.width = "100%";
      wrap.style.height = getMaxHeight();
      wrap.className += " " + fullscreen_classname;
      document.documentElement.style.overflow = "hidden";
    } else {
      wrap.className = wrap.className
        .replace(new RegExp("\\s*" + fullscreen_classname + "\\b"), "");
      document.documentElement.style.overflow = "";
      wrap.style.width = info.width;
      wrap.style.height = getMaxHeight(wrap);
      window.scrollTo(info.scrollLeft, info.scrollTop);
    }
    return { height: wrap.style.height, width: wrap.style.width };
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
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("put", "jio_put")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("redirect", "redirect")

    .allowPublicAcquisition('setFillStyle', function () {
      return setFillStyle(this);
    })

    .declareMethod('setFillStyle', function () {
      return setFillStyle(this);
    })

    .allowPublicAcquisition('triggerMaximize', function () {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return switchMaximizeMode(gadget);
        })
        .fail(function (e) {
          console.log(e);
        });
    })

    .allowPublicAcquisition('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })

    .declareMethod('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;

      return gadget.jio_get(options.jio_key)
        .push(function (doc) {
          gadget.options.doc = doc;
          gadget.options.doc.title = gadget.options.doc.title || "";
          return new RSVP.Queue()
            .push(function () {
              return gadget.translateHtml(template(options.doc));
            })
            .push(function (html) {
              gadget.props.element.innerHTML = html;
              return gadget.updateHeader({
                page_title: options.doc.title + " | " + options.doc.portal_type,
                back_url: "#page=" +
                    options.doc.portal_type.toLowerCase() + "_list",
                panel_action: false,
                // breadcrumb_url: all_result[4],
                save_action: true
              });
            })
            .push(function () {
              return gadget.props.deferred.resolve();
            });
        });
    })

    /////////////////////////////////////////
    // Render text content gadget
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          // Can be used to retrieve the format or a dedicated element
          // return gadget.jio_getAttachment(gadget.options.jio_key, "html");
          return gadget.jio_getAttachment(gadget.options.jio_key, "img2.png");
        })
        .push(function (data) {
          console.log(data);
          return jIO.util.readBlobAsDataURL(data);
        })
        .push(function (dataurl) {
          var element = gadget.props.element.querySelector(".document-preview"),
          iframe;
          iframe = document.createElement('iframe');
          iframe.setAttribute('src', dataurl.target.result);
          element.appendChild(iframe);
          gadget.setFillStyle();
          return true;
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
              return saveContent(gadget, event);
            }
          );
        });
    });

}(window, document, RSVP, rJS, Handlebars, loopEventListener, jIO));