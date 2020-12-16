/*globals window, document, RSVP, rJS, XMLHttpRequest, DOMParser, URL,
          loopEventListener, history */
/*jslint indent: 2, maxlen: 80*/
(function (window, document, RSVP, rJS, XMLHttpRequest, DOMParser, URL,
          loopEventListener, history) {
  "use strict";

  // XXX Copy/paste from renderjs
  function ajax(url) {
    var xhr;
    function resolver(resolve, reject) {
      function handler() {
        try {
          if (xhr.readyState === 0) {
            // UNSENT
            reject(xhr);
          } else if (xhr.readyState === 4) {
            // DONE
            if ((xhr.status < 200) || (xhr.status >= 300) ||
                (!/^text\/html[;]?/.test(
                  xhr.getResponseHeader("Content-Type") || ""
                ))) {
              reject(xhr);
            } else {
              resolve(xhr);
            }
          }
        } catch (e) {
          reject(e);
        }
      }

      xhr = new XMLHttpRequest();
      xhr.open("GET", url);
      xhr.onreadystatechange = handler;
      xhr.setRequestHeader('Accept', 'text/html');
      xhr.withCredentials = true;
      xhr.send();
    }
    function canceller() {
      if ((xhr !== undefined) && (xhr.readyState !== xhr.DONE)) {
        xhr.abort();
      }
    }
    return new RSVP.Promise(resolver, canceller);
  }

  function removeHash(url) {
    var index = url.indexOf('#');
    if (index > 0) {
      url = url.substring(0, index);
    }
    return url;
  }

  function scrollToHash(hash) {
    var scroll_element = null;

    if (hash) {
      hash = hash.split('#', 2)[1];
      if (hash === undefined) {
        hash = "";
      }
      if (hash) {
        scroll_element = document.querySelector(hash);
      }
    }

    if (scroll_element === null) {
      window.scrollTo(0, 0);
    } else {
      scroll_element.scrollIntoView(true);
    }

  }

  function parseLanguageElement(language_element) {
    var language_list = [],
      li_list = language_element.querySelectorAll('a'),
      i;
    for (i = 0; i < li_list.length; i += 1) {
      language_list.push({
        href: li_list[i].href,
        text: li_list[i].hreflang
      });
    }
    return language_list;
  }

  function parseSitemapElement(sitemap_element) {
    var a = sitemap_element.querySelector('a'),
      sitemap = {
        href: a.href,
        text: a.textContent,
        child_list: []
      },
      ul = a.nextElementSibling,
      li_list,
      i;

    if (ul === null) {
      li_list = [];
    } else {
      li_list = ul.children;
    }
    for (i = 0; i < li_list.length; i += 1) {
      sitemap.child_list.push(parseSitemapElement(li_list[i]));
    }
    return sitemap;
  }

  function parseFormElement(form_element) {
    var result;
    if (form_element !== null) {
      return form_element.outerHTML;
    }
    return result;
  }

  function parseStatusMessage(status_element, information_element) {
    var result = "";
    if (status_element !== null) {
      result = status_element.textContent;
    }
    if (information_element !== null) {
      result = information_element.textContent;
    }
    return result;
  }

  function parsePageContent(body_element) {
    return {
      html_content: body_element.querySelector('main').innerHTML,
      language_list: parseLanguageElement(
        body_element.querySelector('nav#language')
      ),
      sitemap: parseSitemapElement(
        body_element.querySelector('nav#sitemap')
      ),
      form_html_content: parseFormElement(
        body_element.querySelector('form#main_form')
      ),
      portal_status_message: parseStatusMessage(
        body_element.querySelector('p#portal_status_message'),
        body_element.querySelector('p#information_area')
      ),
    };
  }

  function renderPage(gadget, page_url, hash) {
    return new RSVP.Queue(RSVP.hash({
      xhr: ajax(page_url),
      style_gadget: gadget.getDeclaredGadget('renderer')
    }))
      .push(function (result_dict) {
        var dom_parser = (new DOMParser()).parseFromString(
          result_dict.xhr.responseText,
          'text/html'
        ),
          parsed_content = parsePageContent(dom_parser.body);
        gadget.parsed_content = parsed_content;
        parsed_content.page_title = dom_parser.title;
        return result_dict.style_gadget.render(parsed_content.html_content,
                                               parsed_content);
      })
      .push(function () {
        return scrollToHash(hash);
      });
  }

  function isAnotherSitemapLocation(sitemap, url1, url2) {
    var is_url1_matching = (url1.indexOf(sitemap.href) === 0),
      is_child_another_location,
      i;
    if (is_url1_matching && (url2.indexOf(sitemap.href) !== 0)) {
      return true;
    }
    if (!is_url1_matching) {
      // Both url do not match
      return false;
    }
    // If both match, check sub urls
    for (i = 0; i < sitemap.child_list.length; i += 1) {
      is_child_another_location = isAnotherSitemapLocation(
        sitemap.child_list[i],
        url1,
        url2
      );
      if (is_child_another_location) {
        return true;
      }
    }
    return false;
  }


  function listenURLChange() {
    var gadget = this;

    // prevent automatic page location restoration
    if (history.scrollRestoration) {
      history.scrollRestoration = 'manual';
    }

    function handlePopState() {
      return renderPage(gadget, window.location.href, window.location.hash);
    }

    function handleClick(evt) {
      var target_element = evt.target.closest('a'),
        base_uri = document.baseURI,
        link_url,
        matching_language_count = 0,
        matching_language_base_uri_count = 0;

      if (!target_element) {
        // Only handle link
        return;
      }
      if (target_element.target === "_blank") {
        // Open in a new tab
        return;
      }
      if (evt.altKey || evt.ctrlKey || evt.metaKey || evt.shiftKey) {
        return;
      }

      link_url = new URL(target_element.href, base_uri);
      if (link_url.href.indexOf(base_uri) !== 0) {
        // Only handle sub path of the base url
        // Meaning it will also reload when going from a non default language
        // to the default one
        return;
      }

      // Check if going from the default language to another one
      // Check if url is suburl from 2 languages (default + the expected one)
      gadget.parsed_content.language_list.map(function (language) {
        if (link_url.href.indexOf(language.href) === 0) {
          matching_language_count += 1;
        }
        // Ensure current url is in the default language
        if (base_uri.indexOf(language.href) === 0) {
          matching_language_base_uri_count += 1;
        }
      });
      if ((1 < matching_language_count) &&
          (matching_language_base_uri_count === 1)) {
        return;
      }

      // Check if going from a section to a child one
      if (isAnotherSitemapLocation(gadget.parsed_content.sitemap,
                                   link_url.href, base_uri)) {
        return;
      }

      if (link_url.hash) {
        // If new link has an hash, check if the path/query parts are identical
        // if so, do not refresh the content and
        // let browser scroll to the correct element
        if (removeHash(link_url.href) === removeHash(window.location.href)) {
          return;
        }
      }

      evt.preventDefault();
      return renderPage(gadget, target_element.href, link_url.hash)
        .push(function () {
          // Important: pushState must be called AFTER the page rendering
          // to ensure popstate listener is correctly working
          // when the user will click on back/forward browser buttons
          history.pushState(null, null, target_element.href);
        }, function () {
          // Implement support for managed error
          // (like URL is not an HTML document parsable)
          // and redirect in such case
          window.location = target_element.href;
        });
    }

    return RSVP.all([
      loopEventListener(window, 'popstate', false, handlePopState, false),
      loopEventListener(gadget.element, 'click', false, handleClick,
                        false)
    ]);
  }

  rJS(window)
    .allowPublicAcquisition("reportServiceError", function () {
      this.element.hidden = false;
      throw rJS.AcquisitionError();
    })
    .declareJob("listenURLChange", listenURLChange)
    .declareService(function () {
      var gadget = this,
        style_gadget,
        body = gadget.element,
        style_gadget_url = body.getAttribute("data-nostyle-gadget-url"),
        parsed_content;

      if (!style_gadget_url) {
        // No style configured, use backend only rendering
        return rJS.declareCSS("jsstyle.css", document.head);
      }

      parsed_content = parsePageContent(gadget.element);
      gadget.parsed_content = parsed_content;
      parsed_content.page_title = document.title;
      // Clear the DOM
      while (body.firstChild) {
        body.firstChild.remove();
      }
      return gadget.declareGadget(style_gadget_url, {scope: 'renderer'})
        .push(function (result) {
          style_gadget = result;
          return style_gadget.render(parsed_content.html_content,
                                     parsed_content);
        })
        .push(function () {
          // Trigger URL handling
          gadget.listenURLChange();

          body.appendChild(style_gadget.element);
          gadget.element.hidden = false;
          scrollToHash(window.location.hash);
        }, function (error) {
          gadget.element.hidden = false;
          throw error;
        });
    });

}(window, document, RSVP, rJS, XMLHttpRequest, DOMParser, URL,
  loopEventListener, history));