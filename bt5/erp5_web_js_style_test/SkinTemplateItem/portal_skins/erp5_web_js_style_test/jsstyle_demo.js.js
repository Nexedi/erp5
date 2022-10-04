/*globals window, document, rJS, domsugar, URL*/
/*jslint indent: 2, maxlen: 80*/
(function (window, document, rJS, domsugar, URL) {
  "use strict";

  function changeAltLoad(evt) {
    evt.target.alt = 'loaded';
  }

  function changeAltError(evt) {
    evt.target.alt = 'error';
  }

  function renderSitemap(sitemap, element) {
    var child_list = [],
      i;
    for (i = 0; i < sitemap.child_list.length; i += 1) {
      child_list.push(
        renderSitemap(sitemap.child_list[i], domsugar('li'))
      );
    }
    if (child_list.length !== 0) {
      child_list = [domsugar('ol', child_list)];
    }
    child_list.unshift(domsugar('a', {
      text: sitemap.text,
      href: sitemap.href
    }));
    return domsugar(element, child_list);
  }

  rJS(window)
    .setState({
      render_count: 0
    })
    .ready(function () {
      var gadget = this;
      // Check if the gadget is reloaded when changing the language
      return gadget.getPath()
        .push(function (url) {
          return gadget.changeState({gadget_style_url: url});
        });
    })
    .declareMethod("render", function (html_content, parsed_content) {
      var state = {
        feed_url: parsed_content.feed_url || "",
        document_list: JSON.stringify(parsed_content.document_list || []),
        current_language: parsed_content.language || "",
        language_list: JSON.stringify(parsed_content.language_list || []),
        sitemap: JSON.stringify(parsed_content.sitemap || {}),
        page_title: parsed_content.page_title || "",
        portal_status_message: parsed_content.portal_status_message || "",
        form_html_content: parsed_content.form_html_content,
        html_content: html_content || "",
        render_count: this.state.render_count + 1
      };
      return this.changeState(state);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        language_list,
        document_list,
        child_list,
        i,
        web_page_element,
        element_list,
        element,
        new_element,
        feed_url;

      if (modification_dict.hasOwnProperty('page_title')) {
        document.title = gadget.state.page_title;
      }
      if (modification_dict.hasOwnProperty('portal_status_message')) {
        domsugar(gadget.element.querySelector('p#portal_status_message'), {
          text: gadget.state.portal_status_message
        });
      }
      if ((modification_dict.hasOwnProperty('form_html_content')) ||
          (modification_dict.hasOwnProperty('html_content'))) {
        if (gadget.state.form_html_content) {
          // In case of form, display it directly
          domsugar(gadget.element.querySelector('main'), {
            html: gadget.state.form_html_content
          });
        } else {

          // Try to find the Web Page content only
          web_page_element = domsugar('div', {html: gadget.state.html_content})
                                     .querySelector('div.input').firstChild;

          // Replace IMG src value, to disable the browser cache
          // and force downloading it.
          // Used by test to check if original url has been accessed
          element_list = web_page_element.querySelectorAll('img');
          for (i = 0; i < element_list.length; i += 1) {
            element = element_list[i];
            feed_url = new URL(element.getAttribute('src'),
                               window.location.href);
            feed_url.search = feed_url.search + '&cachevalue=foo';
            // Not renderJS friendly, but that's only for the test...
            element.addEventListener('load', changeAltLoad);
            element.addEventListener('error', changeAltError);
            element.src = feed_url.href;
          }

          domsugar(gadget.element.querySelector('main'), [
            web_page_element
          ]);
        }
      }
      if (modification_dict.hasOwnProperty('gadget_style_url')) {
        domsugar(gadget.element.querySelector('p#gadget_style_url'), {
          text: gadget.state.gadget_style_url
        });
      }
      if (modification_dict.hasOwnProperty('render_count')) {
        domsugar(gadget.element.querySelector('p#render_count'), {
          text: 'render count: ' + gadget.state.render_count
        });
      }
      if (modification_dict.hasOwnProperty('current_language')) {
        domsugar(gadget.element.querySelector('p#current_language'), {
          text: gadget.state.current_language
        });
      }
      if (modification_dict.hasOwnProperty('feed_url')) {
        domsugar(gadget.element.querySelector('p#feed_url'), {
          text: gadget.state.feed_url
        });
      }
      if (modification_dict.hasOwnProperty('language_list')) {
        language_list = JSON.parse(gadget.state.language_list);
        child_list = [];
        for (i = 0; i < language_list.length; i += 1) {
          child_list.push(domsugar('li', [domsugar('a', {
            text: language_list[i].text,
            href: language_list[i].href
          })]));
        }
        domsugar(gadget.element.querySelector('nav#language'),
                 [domsugar('ul', child_list)]);
      }
      if (modification_dict.hasOwnProperty('document_list')) {
        document_list = JSON.parse(gadget.state.document_list);
        child_list = [];
        for (i = 0; i < document_list.length; i += 1) {
          child_list.push(domsugar('li', [
            domsugar('a', {
              text: document_list[i].text,
              href: document_list[i].href
            }),
            domsugar('p', {text: 'Author: ' + document_list[i].author}),
            domsugar('p', {text: 'Description: ' +
                                 document_list[i].description}),
            domsugar('p', {text: 'Date: ' + document_list[i].date})
          ]));
        }
        domsugar(gadget.element.querySelector('aside#document_list'),
                 [domsugar('ul', child_list)]);
      }
      if (modification_dict.hasOwnProperty('sitemap')) {
        renderSitemap(JSON.parse(gadget.state.sitemap),
                      gadget.element.querySelector('nav#sitemap'));
      }
    });

}(window, document, rJS, domsugar, URL));