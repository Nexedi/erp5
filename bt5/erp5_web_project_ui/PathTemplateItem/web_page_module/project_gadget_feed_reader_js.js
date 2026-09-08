/*global window, rJS, RSVP, domsugar, jIO, URL */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, RSVP, domsugar, jIO, URL) {
  "use strict";

  function compareParsedItem(a, b) {
    if (a.index < b.index) {
      return 1;
    }
    if (a.index > b.index) {
      return -1;
    }
    return 0;
  }

  function formatDate(date) {
    return ('0' + date.getHours()).substr(-2) + ':' +
      ('0' + date.getMinutes()).substr(-2);
  }

  function formatDay(date) {
    var yyyy = date.getFullYear().toString(),
      mm = (date.getMonth() + 1).toString(),
      dd  = date.getDate().toString();
    return yyyy + '-' + (mm[1] ? mm : "0" + mm[0]) + '-' +
           (dd[1] ? dd : "0" + dd[0]);
  }

  function cleanText(text) {
    var limit = 280,
      suffix = '\u2026';
    if (text.length > limit) {
      text = text.slice(0, limit).trim();
      text = text.slice(0, text.lastIndexOf(' '));
      text = text + suffix;
    }
    return text;
  }

  function cleanHTMLText(text) {
    text = rJS.parseDocumentStringOrFail(text, 'text/html')
                          .querySelector("body")
                          .textContent;
    return cleanText(text);
  }

  function parseItem(item, rss_url, rss_title) {

    var result = {},
      element_guid = item.querySelector("guid"),
      element_enclosure = item.querySelector("enclosure"),
      element_link = item.querySelector("link"),
      element_comment = item.querySelector('comments'),
      element_source = item.querySelector('source'),
      element_title = item.querySelector("title"),
      element_description = item.querySelector("description"),
      element_publication_date = item.querySelector("pubDate");

    // guid
    if (element_guid !== null) {
      result.guid = {};
      if (element_guid.getAttribute("isPermaLink") !== "false") {
        result.guid.is_permalink = "true";
      }
      result.guid.text = element_guid.textContent;
      if (result.guid.text === "") {
        delete result.guid;
      } else if (!result.guid.is_permalink) {
        delete result.guid;
      } else {
        result.hasheader = true;
      }
    }

    // comments
    if (element_comment !== null) {
      result.comments = element_comment.textContent;
      if (result.comments === "") {
        delete result.comments;
      }
    }

    // enclosure
    if (element_enclosure !== null) {
      result.enclosure = {
        url: element_enclosure.getAttribute("url"),
        length: element_enclosure.getAttribute("length") || "",
        type: element_enclosure.getAttribute("type") || ""
      };
      if (result.enclosure.url === "") {
        delete result.enclosure;
      } else {
        result.hasheader = true;
      }
    }

    // source
    if (element_source === null) {
      // Use feed URL as source
      result.source = {
        url: rss_url,
        title: rss_title
      };
      result.hasheader = true;
    } else {
      result.source = {
        url: element_source.getAttribute("url"),
        title: element_source.textContent
      };

      if (result.source.url === "") {
        delete result.source;
      } else {
        result.hasheader = true;
      }
    }

    // publication date
    if (element_publication_date !== null) {
      // XXX
      result.date = element_publication_date.textContent;
      if (result.date === "") {
        delete result.date;
      } else {
        result.date = Date.parse(result.date);
        if (isNaN(result.date)) {
          delete result.date;
        } else {
          result.date = new Date(result.date);
        }
      }
    }
    if (result.date === undefined) {
      result.index = "0000";
    } else {
      result.index = result.date.toISOString();
      result.date_title = formatDate(result.date);
      result.hasheader = true;
    }

    // link
    if (element_link !== null) {
      result.link = element_link.textContent;
      if (result.link === "") {
        delete result.link;
      }

      if (result.guid !== undefined) {
        if (result.link === result.guid.text) {
          delete result.guid;
        }
      }

    }

    if ((result.link === undefined) && (result.guid !== undefined)) {
      result.link = result.guid.text;
      delete result.guid;
    }
    if ((result.link === undefined) && (result.comments !== undefined)) {
      result.link = result.comments;
      delete result.comments;
    }
    if ((result.guid === undefined) && (result.comments !== undefined)) {
      result.guid = {text: result.comments};
      delete result.comments;
    }

    if (result.guid !== undefined) {
      // Drop guid link nearly identical from link (#comments)
      if (result.guid.text.indexOf(result.link) === 0) {
        delete result.guid;
      }
    }

    if (result.link !== undefined) {
      result.hasheader = true;
    }

    // title and description
    if ((element_title !== null) && (element_description !== null)) {
      result.title = cleanText(element_title.textContent);
      // XXX property name
      result.content = cleanHTMLText(element_description.textContent);
      if ((result.title === result.content) || (!result.content)) {
        delete result.content;
      }
    } else if ((element_title === null) && (element_description !== null)) {
      result.title = cleanHTMLText(element_description.textContent);
    } else if (element_title !== null) {
      result.title = cleanText(element_title.textContent);
    }
    if (result.title === "") {
      delete result.title;
    }

    if (result.title !== undefined) {
      return result;
    }
    return;
  }


  rJS(window)
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    .declareMethod('render', function (options) {
      return this.changeState(options);
    })

    .onStateChange(function () {
      var gadget = this;
      if (!gadget.state.feed_url) {
        // gadget doesn't know which URL to call
        return undefined;
      }
      return gadget.renderAsynchonous();
    })

    .declareJob('renderAsynchonous', function () {
      // Ensure the ajax call is done in a service,
      // to not block the full UI
      var gadget = this;

      return new RSVP.Queue(jIO.util.ajax({
        type: "GET",
        url: gadget.state.feed_url,
        xhrFields: {
          withCredentials: true,
          Accept: "application/rss+xml;q=0.9"
        }
      }))
        .push(function (evt) {
          var rss_xml = rJS.parseDocumentStringOrFail(
            evt.target.response,
            "application/xml"
          ),
            rss_title = rss_xml.querySelector("title"),
            item_list,
            len,
            i,
            parsed_item,
            news_list = [],
            second_news_list = [],
            href_promise_list = [],
            news_link_dict = {};

          // Main feed title
          if (rss_title === null) {
            rss_title = 'Unknown feed';
          } else {
            rss_title = rss_title.textContent;
          }

          // Feed entries
          item_list = rss_xml.getElementsByTagName("item");
          len = item_list.length;
          for (i = 0; i < len; i += 1) {
            parsed_item = parseItem(item_list[i],
                                    gadget.state.feed_url,
                                    rss_title);
            if (parsed_item !== undefined) {
              news_list.push(parsed_item);
            }
          }
          news_list.sort(compareParsedItem);

          // Calculate all entries links inside erp5js
          len = news_list.length;
          for (i = 0; i < len; i += 1) {
            // Drop the old entries linking to an already linked entry
            // The goal is to only display the latest message related to a topic
            // (support request for example)
            // and let user click to see the details displayed in a cleaner way
            if (news_list[i].hasOwnProperty('link')) {
              if (!news_link_dict.hasOwnProperty(news_list[i].link)) {
                second_news_list.push(news_list[i]);

                if (news_list[i].link) {
                  // Drop if there if already linked
                  news_link_dict[news_list[i].link] = true;
                  href_promise_list.push({
                    command: 'push_history',
                    options: {
                      // XXX probably a hack
                      // Assume all links uses erp5js router logic
                      jio_key: (new URL(news_list[i].link)).hash
                                .split('?')[0].split('#/', 2)[1]
                    }
                  });
                } else {
                  // No link was provided by the backend
                  // As getUrlForList probably does not support no command info
                  // (this leads to the error command)
                  // reload the page by default
                  // This is probably confusing for end user,
                  // but we expect this case to not occurs often
                  href_promise_list.push({
                    command: 'reload'
                  });
                }
              }
            }
          }

          return RSVP.hash({
            news_list: second_news_list,
            href_list: gadget.getUrlForList(href_promise_list)
          });
        })

        .push(function (hash) {
          var news_list = hash.news_list,
            href_list = hash.href_list,
            len,
            i,
            current_day,
            previous_day,
            child_list = [],
            p_child_container,
            p_child_list = [];

          // Render all entries
          len = news_list.length;
          for (i = 0; i < len; i += 1) {

            if (news_list[i].date === undefined) {
              current_day = "No date";
            } else {
              current_day = formatDay(news_list[i].date);
            }
            if ((i === 0) || (previous_day !== current_day)) {
              previous_day = current_day;
              child_list.push(domsugar('section', {
                'class': 'ui-content-header-plain',
                text: current_day
              }));
              p_child_container = domsugar('ul',
                                           {'class': 'document-listview'});
              child_list.push(p_child_container);
            }
            p_child_list = [];

            p_child_list.push(domsugar(null, {text: news_list[i].title}));

            if (news_list[i].hasOwnProperty('content')) {
              p_child_list.push(domsugar('br'), domsugar('i', [
                domsugar('small', {text: news_list[i].content})
              ]));
            }

            if (news_list[i].hasOwnProperty('date_title')) {
              p_child_list.push(' ', domsugar(
                'span',
                {'class': 'ui-li-count'},
                [
                  domsugar('time', {
                    'class': 'dt-published',
                    datetime: news_list[i].date_title,
                    text: news_list[i].date_title
                  })
                ]
              ));
            }

            p_child_container.appendChild(
              domsugar('li', {'class': 'ui-li-has-count'}, [
                domsugar('a', {href: href_list[i]}, p_child_list)
              ])
            );


          }

          if (child_list.length === 0) {
            domsugar(gadget.element,
                     [domsugar('p', {text: 'No news.'})]);
          } else {
            domsugar(gadget.element, child_list);
          }

        });

    });
}(window, rJS, RSVP, domsugar, jIO, URL));