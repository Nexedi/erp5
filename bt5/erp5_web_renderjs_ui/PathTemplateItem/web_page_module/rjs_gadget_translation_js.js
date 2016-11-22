/*global document, window, rJS, translation_data, RSVP */
/*jslint nomen: true, indent: 2 */
(function (document, window, rJS, translation_data, RSVP) {
  "use strict";

  function translate(string, gadget) {
    if (translation_data[gadget.state.language]) {
      return translation_data[gadget.state.language][string] || string;
    }
    return string;
  }

  // translate a list of elements passed and returned as string
  function translateHtml(string, gadget) {
    var temp, element_list, i, i_len, element, lookup, translate_list, target,
      route_text, has_breaks, l, l_len, j, j_len;
    // NOTE: <div> cannot be used for everything... (like table rows)
    // XXX: currently I only update where needed. Eventually all calls to
    // translateHtml should pass "their" proper wrapping element
    temp = document.createElement("div");
    temp.innerHTML = string;

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
            element.setAttribute(target[0].substr(1), translate(target[1], gadget));
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
              element.previousSibling.textContent = translate(target[1], gadget);
            }
            element.value = translate(target[1], gadget);
            break;
          case "[parent":
            element.parentNode.childNodes[0].textContent =
                translate(target[1], gadget);
            break;
          case "[node":
            element.childNodes[0].textContent = translate(target[1], gadget);
            break;
          case "[last":
            // if null, append, if textnode replace, if span, appned
            if (element.lastChild && element.lastChild.nodeType === 3) {
              element.lastChild.textContent = translate(target[1], gadget);
            } else {
              element.appendChild(document.createTextNode(translate(target[1], gadget)));
            }
            break;
          case "[html":
            element.innerHTML = translate(target[1], gadget);
            break;
          default:
            if (element.hasChildNodes()) {
              for (j = 0, j_len = element.childNodes.length; j < j_len; j += 1) {
                if (element.childNodes[j].nodeType === 3) {
                  element.childNodes[j].textContent = translate(translate_list[l], gadget);
                }
              }
            } else {
              element.textContent = translate(translate_list[l], gadget);
            }
            break;
          }
        }
      }
    }
    // return string
    return temp.innerHTML;
  }

  rJS(window)
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareMethod('translate', function (string) {
      // XXX Allow to change the language
      var gadget = this;
      if (!gadget.state.language) {
        return new RSVP.Queue()
          .push(function () {
            return RSVP.all([
              gadget.getSetting("selected_language"),
              gadget.getSetting("default_selected_language")
            ]);
          })
          .push(function (results) {
            gadget.state.language = results[0] || results[1];
            return translate(string, gadget);
          });
      }
      return translate(string, gadget);
    })

    .declareMethod('translateHtml', function (string) {
      var gadget = this;
      if (!gadget.state.language) {
        return new RSVP.Queue()
          .push(function () {
            return RSVP.all([
              gadget.getSetting("selected_language"),
              gadget.getSetting("default_selected_language")
            ]);
          })
          .push(function (results) {
            gadget.state.language = results[0] || results[1];
            return translateHtml(string, gadget);
          });
      }
      return translateHtml(string, gadget);
    });

}(document, window, rJS, translation_data, RSVP));
