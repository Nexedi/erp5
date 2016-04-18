/*global document, window, rJS, translation_data */
/*jslint nomen: true, indent: 2 */
(function (document, window, rJS, translation_data) {
  "use strict";

  function translate(gadget,string) {
   // var language = gadget.getSetting('language');
   var language;
    return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('language'),
          ]);
        })
        .push(function (setting_list) {
      
     language=setting_list; 
    });
    console.log("test");
    console.log(language);

    if (language === undefined){
               language = 'zh';

        gadget.setSetting('language','zh');

    }
    return translation_data[language][string] || string;
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (gadget) {
      gadget.property_dict = {};
    })
  
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")

    .declareMethod('translate', function (string) {
      // XXX Allow to change the language
      return translate(this,string);
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
      // XXX: currently I only update where needed. Eventually all calls to
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
              element.setAttribute(target[0].substr(1), translate(gadget,target[1]));
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
                element.previousSibling.textContent = translate(gadget,target[1]);
              }
              element.value = translate(gadget,target[1]);
              break;
            case "[parent":
              element.parentNode.childNodes[0].textContent =
                  translate(gadget,target[1]);
              break;
            case "[node":
              element.childNodes[0].textContent = translate(gadget,target[1]);
              break;
            case "[last":
              // if null, append, if textnode replace, if span, appned
              if (element.lastChild && element.lastChild.nodeType === 3) {
                element.lastChild.textContent = translate(gadget,target[1]);
              } else {
                element.appendChild(document.createTextNode(translate(gadget,target[1])));
              }
              break;
            case "[html":
              element.innerHTML = translate(gadget,target[1]);
              break;
            default:
              // NOTE: be careful of emptying elements with children!
              while (element.hasChildNodes()) {
                element.removeChild(element.lastChild);
              }
              element.appendChild(document.createTextNode(translate(gadget,translate_list[l])));
              element.appendChild(document.createElement("span"));
              break;
            }
          }
        }
      }
      // return string
      return temp.innerHTML;
    });

}(document, window, rJS, translation_data));
