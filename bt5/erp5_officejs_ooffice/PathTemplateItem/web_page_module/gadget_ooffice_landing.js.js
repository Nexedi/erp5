/*global window, rJS, jIO, URI, location, console, document, RSVP, loopEventListener, navigator, XMLHttpRequest, ProgressEvent*/
/*jslint nomen: true, indent: 2*/
(function (window, rJS, jIO) {
  "use strict";

  function this_func_link(name) {
    return function (opt) {
      return this[name].apply(this, opt);
    };
  }

  var gadget_klass = rJS(window),
    SCOPE = "main",
    SETTING_STORAGE = jIO.createJIO({
      type: "indexeddb",
      database: "setting"
    });


  gadget_klass

    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getElement()
        .push(function (element) {
          var element_list =
              element.querySelectorAll("[data-renderjs-configuration]"),
            len = element_list.length,
            key,
            value,
            i;
          gadget.props.element = element;
          gadget.props.configuration = {};
          for (i = 0; i < len; i += 1) {
            key = element_list[i].getAttribute('data-renderjs-configuration');
            value = element_list[i].textContent;
            gadget.props.configuration[key] = value;
          }
        })
        .push(function () {
          // Resources are now ready
          // Modify base to provides same base as gadget
          var base = document.createElement('base'),
            child_gadget_url = gadget.props.configuration["child-gadget"];
          base.href = new URI(child_gadget_url + '/../').normalize()
            .toString();
          document.head.appendChild(base);
          return gadget.declareGadget(
            child_gadget_url,
            {
              scope: SCOPE
            }
          );
        })
        .push(function (child_gadget) {
          return child_gadget.getElement();
        })
        .push(function (child_element) {
          gadget.props.element.appendChild(child_element);
        });
    })
    .declareMethod('getSetting', function (key, default_value) {
      var from_html = this.props.configuration[key];
      if (from_html) {
        return from_html;
      }
      return SETTING_STORAGE.get("setting")
        .push(function (doc) {
          return doc[key] || default_value;
        }, function (error) {
          if (error.status_code === 404) {
            return default_value;
          }
          throw error;
        });
    })
    .allowPublicAcquisition('getSetting', this_func_link('getSetting'))
    .declareMethod('setSetting', function (key, value) {
      return SETTING_STORAGE.get("setting")
        .push(undefined, function (error) {
          if (error.status_code === 404) {
            return {};
          }
          throw error;
        })
        .push(function (doc) {
          doc[key] = value;
          return SETTING_STORAGE.put('setting', doc);
        });
    })
    .allowPublicAcquisition('setSetting', this_func_link('setSetting'))
    .declareAcquiredMethod("triggerSubmit", "triggerSubmit")
    .allowPublicAcquisition('triggerSubmit', this_func_link('triggerMaximize'))
    .declareAcquiredMethod("triggerMaximize", "triggerMaximize")
    .allowPublicAcquisition('triggerMaximize', this_func_link('triggerMaximize'))
    .declareMethod('render', function (options) {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget(SCOPE);
        })
        .push(function (child_gadget) {
          return child_gadget.render(options);
        });
    })
    .declareMethod('getContent', function () {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget(SCOPE);
        })
        .push(function (child_gadget) {
          return child_gadget.getContent();
        });
    });

}(window, rJS, jIO));