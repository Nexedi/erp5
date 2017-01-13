/*jslint indent: 2, maxlen: 80, nomen: true, todo: true, unparam:true*/
/*global window, rJS, document, i18n, UriTemplate, fetchLanguage, RSVP*/
(function (window, rJS, i18n, UriTemplate) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Some methods
  /////////////////////////////////////////////////////////////////
  function getTranslationDict(my_gadget, my_language) {
    var props = my_gadget.property_dict,
      cookie_lang = fetchLanguage(),
      lang = cookie_lang || props.default_language || my_language,
      path =  props.src + "?language=" + lang + "&namespace=dict";
    return new RSVP.Queue()
      .push(function () {
        return my_gadget.jio_getAttachment({
          "_id": "erp5",
          "_attachment": path
        });
      })
      .push(function (my_event) {
        return my_event.data;
      });
  }

  // XXX: language definitions are not standard compliant!
  // "zh-CN" is a language, "zh" is not, browser will return the "zh-CN"
  // on internal i18n methods, which requires this method to "fix"
  function fetchLanguage() {
    var lang = i18n.detectLanguage();
    if (lang.length > 2) {
      return lang.substring(0, 2);
    }
    return lang;
  }

  /////////////////////////////////////////////////////////////////
  // Gadget behaviour
  /////////////////////////////////////////////////////////////////
  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////

    // retrieve initializatin and web site properties
    // XXX: This takes too long for header and sometimes for panel as both
    // run things on .ready() = outside chain (eg. calling header.render() on 
    // header .ready())
    // XXX: Header "fixable" by adding notifyUpdate
    .ready(function (my_gadget) {
      my_gadget.property_dict = {};

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            my_gadget.getSiteRoot(),
            my_gadget.getTranslationMethod()
          ]);
        })
        .push(function (my_config_list) {
          var url;
          url = my_config_list[0]
          my_gadget.property_dict.src = my_config_list[1];
          return my_gadget.jio_getAttachment({
            "_id": "erp5",
            "_attachment": url
          });
        })
        .push(function (my_hateoas) {
          var url;
          // NOTE: at this point createJIO has not been called yet, so allDocs
          // is not available and must be called "manually"
          // XXX: Improve
          url = UriTemplate.parse(my_hateoas.data._links.raw_search.href)
            .expand({
              query: 'portal_type: "Web Site" AND title: "'
                + my_hateoas.data._links.parent.name  + '"',
              select_list: [
                "available_language_set",
                "default_available_language"
              ],
              limit: [0, 1]
            });

          return my_gadget.jio_getAttachment({
            "_id": "erp5",
            "_attachment": url
          });
        })
        .push(function (my_site_configuration) {
          var web_site = my_site_configuration.data._embedded.contents[0];
          // set remaining properties
          my_gadget.property_dict.language_list =
            web_site.available_language_set;
          my_gadget.property_dict.default_language =
            web_site.default_available_language;
        });
    })

    // Fetch first dict here, based on info retrieved from ERP5 website object
    .ready(function (my_gadget) {
      var props = my_gadget.property_dict;
      // skip if translations are not available
      if (props.translation_disabled) {
        return my_gadget;
      }

      return new RSVP.Queue()
        .push(function () {
          return getTranslationDict(my_gadget);
        })
        .push(function (my_language_dict) {
          props.current_language_dict = my_language_dict;

          // initialize i18n
          i18n.init({
            "customLoad": function (my_lng, my_ns,
               my_option_dict, my_callback) {
              // translations available now
              my_callback(null, props.current_language_dict);
            },
            //"use_browser_language": true,
            "lng": fetchLanguage() || props.default_language,
            "load": "current",
            "fallbackLng": false,
            "ns": 'dict'
          });
          return my_gadget.notifyUpdate();
        });
    })


    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("notifyUpdate", "notifyUpdate")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getSiteRoot", "getSiteRoot")
    .declareAcquiredMethod("getTranslationMethod", "getTranslationMethod")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    // expose languages to gadget which want to know (eg panel)
    .declareMethod('getLanguageList', function () {
      return JSON.stringify(this.property_dict.language_list);
    })

    .declareMethod('changeLanguage', function (my_new_language) {
      var gadget = this,
        current_language = fetchLanguage();

      // XXX: relies on cookie value set by i18n!
      if (current_language !== my_new_language &&
          gadget.property_dict.translation_disabled === undefined) {
        return RSVP.Queue()
          .push(function () {
            return getTranslationDict(gadget, my_new_language);
          })
          .push(function (my_language_dict) {
            gadget.property_dict.current_language_dict = my_language_dict;
            i18n.setLng(my_new_language);
            // XXX: for now, reload as the language is stored in cookie
            window.location.reload();
            //return gadget.translateElementList();
          });
      }

      return gadget;
    })

    // translate a list of elements passed and returned as string
    .declareMethod('translateHtml', function (my_string) {
      var temp, element_list, i, i_len, element, lookup, translate_list, target,
        route_text, has_breaks, l, l_len, gadget;

      gadget = this;

      // skip if no translations available
      if (gadget.property_dict.translation_disabled) {
        return my_string;
      }

      // NOTE: <div> cannot be used for everything... (like table rows)
      // TODO: currently I only update where needed. Eventually all calls to
      // translateHtml should pass "their" proper wrapping element
      temp = document.createElement("div");
      temp.innerHTML = my_string;

      element_list = temp.querySelectorAll("[data-i18n]");

      for (i = 0, i_len = element_list.length; i < i_len; i += 1) {
        element = element_list[i];
        lookup = element.getAttribute("data-i18n");

        if (lookup) {
          translate_list = lookup.split(";");

          for (l = 0, l_len = translate_list.length; l < l_len; l += 1) {
            target = translate_list[l].split("]");

            switch (target[0]) {
            case "[placeholder":
            case "[alt":
            case "[title":
              element.setAttribute(target[0].substr(1), i18n.t(target[1]));
              break;
            case "[value":
              has_breaks = element.previousSibling.textContent.match(/\n/g);

              // JQM inputs > this avoids calling checkboxRadio("refresh")!
              if (element.tagName === "INPUT") {
                switch (element.type) {
                case "submit":
                case "reset":
                case "button":
                  route_text = true;
                  break;
                }
              }
              if (route_text && (has_breaks || []).length === 0) {
                element.previousSibling.textContent = i18n.t(target[1]);
              }
              element.value = i18n.t(target[1]);
              break;
            case "[parent":
              element.parentNode.childNodes[0].textContent =
                  i18n.t(target[1]);
              break;
            case "[node":
              element.childNodes[0].textContent = i18n.t(target[1]);
              break;
            case "[last":
              // if null, append, if textnode replace, if span, appned
              if (element.lastChild && element.lastChild.nodeType === 3) {
                element.lastChild.textContent = i18n.t(target[1]);
              } else {
                element.appendChild(document.createTextNode(i18n.t(target[1])));
              }
              break;
            case "[html":
              element.innerHTML = i18n.t(target[1]);
              break;
            default:
              // NOTE: be careful of emptying elements with children!
              while (element.hasChildNodes()) {
                element.removeChild(element.lastChild);
              }
              element.appendChild(document.createTextNode(i18n.t(translate_list[l])));
              element.appendChild(document.createElement("span"));
              break;
            }
          }
        }
      }
      // return string
      return temp.innerHTML;
    });
}(window, rJS, i18n, UriTemplate));