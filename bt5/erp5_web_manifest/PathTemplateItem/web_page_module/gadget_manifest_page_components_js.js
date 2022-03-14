/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // api
  /////////////////////////////////////////////////////////////////

  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////

  /////////////////////////////////////////////////////////////////
  // RJS
  /////////////////////////////////////////////////////////////////

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (my_gadget) {
      my_gadget.property_dict = {};
    })

    .ready(function (my_gadget) {
      return my_gadget.getElement()
        .push(function (my_element) {
          my_gadget.property_dict.element = my_element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    // thx https://github.com/jsbin/jsbin/blob/master/docs/embedding.md
    .declareMethod("renderIframe", function (my_form) {
      var relevant_link_list = [my_form],
        className = '',
        innerText,
        i,
        len;

      function findCodeInParent(my_element) {
        var match = my_element;
      
        while (match = match.previousSibling) {
          if (match.nodeName === 'PRE') {
            break;
          }
          if (match.getElementsByTagName) {
            match = match.getElementsByTagName('pre');
            if (match.length) {
              match = match[0]; // only grabs the first
              break;
            }
          }
        }
      
        if (match) {
          return match;
        }
      
        match = my_element.parentNode.getElementsByTagName('pre');
      
        if (!match.length) {
          if (my_element.parentNode) {
            return findCodeInParent(my_element.parentNode);
          } else {
            return null;
          }
        }
      
        return match[0];
      }

      function getQuery(my_querystring) {
        var query = {};
      
        var pairs = my_querystring.split('&'),
            length = pairs.length,
            keyval = [],
            i = 0;
      
        for (; i < length; i++) {
          keyval = pairs[i].split('=', 2);
          try {
            keyval[0] = decodeURIComponent(keyval[0]); // key
            keyval[1] = decodeURIComponent(keyval[1]); // value
          } catch (e) {}
      
          if (query[keyval[0]] === undefined) {
            query[keyval[0]] = keyval[1];
          } else {
            query[keyval[0]] += ',' + keyval[1];
          }
        }
      
        return query;
      }

      function findCode(my_link) {
        var rel = my_link.rel,
          query = my_link.search.substring(1),
          element,
          code;
      
        if (rel && (element = document.getElementById(rel.substring(1)))) {
          code = element[innerText];
        } else {
          // go looking through it's parents
          element = findCodeInParent(my_link);
          if (element) {
            code = element[innerText];
          }
        }
      
        return code;
      }
      
      function detectLanguage(my_code) {
        var htmlcount = (my_code.split("<").length - 1),
          csscount = (my_code.split("{").length - 1),
          jscount = (my_code.split(".").length - 1);
      
        if (htmlcount > csscount && htmlcount > jscount) {
          return 'html';
        } else if (csscount > htmlcount && csscount > jscount) {
          return 'css';
        } else {
          return 'javascript';
        }
      }
      
      function scoop(my_link) {
        var code = findCode(my_link),
          language = detectLanguage(code),
          query = my_link.search.substring(1);
      
        if (language === 'html' && code.toLowerCase().indexOf('<html') === -1) {
          // assume HTML fragment - so try to insert in the %code% position
          language = 'code';
        }
      
        if (query.indexOf(language) === -1) {
          query += ',' + language + '=' + encodeURIComponent(code);
        } else {
          query = query.replace(
            language,
            language + '=' + encodeURIComponent(code)
          );
        }
      
        my_link.search = '?' + query;
      }
      
      function embed(my_link) {
        var iframe = document.createElement('iframe'),
          resize = document.createElement('div'),
          url = my_link.action.replace(/edit/, 'embed'),
          query,
          onmessage;

        iframe.src = url.split('&')[0];
        iframe._src = url.split('&')[0]; // support for google slide embed
        iframe.className = my_link.className; // inherit all classes from link
        iframe.id = my_link.id; // also inherit, give more style control to user
        iframe.style.border = '1px solid #aaa';
      
        //query = getQuery(my_link.search);
        query = {};
        iframe.style.width = query.width || '100%';
        iframe.style.minHeight = query.height || '300px';

        if (query.height) {
          iframe.style.maxHeight = query.height;
        }
        my_link.parentNode.replaceChild(iframe, my_link);

        onmessage = function (event) {
          event || (event = window.event);
          // * 1 to coerse to number, and + 2 to compensate for border
          iframe.style.height = (event.data.height * 1 + 2) + 'px';
        };
      
        if (window.addEventListener) {
          window.addEventListener('message', onmessage, false);
        } else {
          window.attachEvent('onmessage', onmessage);
        }
      }
      
      // start
      if (document.createElement('i').innerText === undefined) {
        innerText = 'textContent';
      } else {
        innerText = 'innerText';
      }

      for (i = 0, len = relevant_link_list.length; i < len; i += 1) {
        className = ' ' + relevant_link_list[i].className + ' ';
        
        if (className.indexOf(' jsbin-scoop ') !== -1) {
          scoop(relevant_link_list[i]);
        } else if (className.indexOf(' jsbin-embed ') !== -1) {
          embed(relevant_link_list[i]);
        }
      }
      
      return {};
    })

    .declareMethod("render", function (option_dict) {
      return this;
    })

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        element = gadget.property_dict.element,
        form_list = element.querySelectorAll('form'),
        loop_list = [],
        i,
        len;

      function formSubmit(e) {
        e.preventDefault();
        gadget.renderIframe(e.target);
        return false;
      }

      // Listen to form submit
      for (i = 0, len = form_list.length; i < len; i += 1) {
        loop_list.push(
          loopEventListener(form_list[i], 'submit', false, formSubmit)
        );
      }
      
      return RSVP.all(loop_list);
    });

}(window, rJS, RSVP, rJS.loopEventListener));
