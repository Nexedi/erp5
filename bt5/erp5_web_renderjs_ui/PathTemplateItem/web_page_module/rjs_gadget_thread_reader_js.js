/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, console, domsugar, Intl, Query, SimpleQuery,
         ComplexQuery*/
(function (window, rJS, RSVP, console, domsugar, Intl, Query, SimpleQuery,
           ComplexQuery) {
  "use strict";

  function createMultipleSimpleOrQuery(key, value_list) {
    var i,
      query_list = [];
    if (!Array.isArray(value_list)) {
      value_list = [value_list];
    }
    for (i = 0; i < value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        operator: "=",
        type: "simple",
        value: value_list[i]
      }));
    }
    if (value_list.len === 1) {
      return query_list[0];
    }
    return new ComplexQuery({
      operator: "OR",
      query_list: query_list,
      type: "complex"
    });
  }

  function getRelativeTimeString(language, current_date, date) {
    var diff,
      abs,
      second = 1000,
      minute = second * 60,
      hour = minute * 60,
      day = hour * 24,
      week = day * 7,
      year = day * 365,
      time_format = new Intl.RelativeTimeFormat(language);

    diff = date - current_date;
    abs = Math.abs(diff);
    // "year", "quarter", "month", "week", "day", "hour", "minute", "second"
    if (abs > year) {
      return time_format.format(Math.floor(diff / year), 'year');
    }
    if (abs > (week * 2)) {
      return time_format.format(Math.floor(diff / week), 'week');
    }
    if (abs > (day * 2)) {
      return time_format.format(Math.floor(diff / day), 'day');
    }
    if (abs > (hour * 2)) {
      return time_format.format(Math.floor(diff / hour), 'hour');
    }
    return time_format.format(Math.floor(diff / minute), 'minute');
  }

  function setPaginationElement(gadget, count, url_list, scroll_to_last_post) {
    var disabled_suffix = ' ui-disabled',
      span_dict,
      first_dict = {
        class: "ui-btn ui-icon-angle-double-left ui-btn-icon-left responsive ui-first-child",
        text: "First"
      },
      previous_dict = {
        class: "ui-btn ui-icon-angle-left ui-btn-icon-left responsive",
        text: "Previous"
      },
      next_dict = {
        class: "ui-btn ui-icon-angle-right ui-btn-icon-right responsive ui-last-child",
        text: "Next"
      };

    if (url_list.length === 0) {
      span_dict = {
        class: "ui-icon-spinner ui-btn-icon-left"
      };
    } else {
      span_dict = {
        text: 'Page ' + Math.ceil((gadget.state.begin_from + count) / gadget.state.lines)
      };
    }

    console.warn(gadget.state);
    if (gadget.state.begin_from === 0) {
      first_dict.class += disabled_suffix;
      previous_dict.class += disabled_suffix;
    } else {
      first_dict.href = url_list[0];
      previous_dict.href = url_list[1];
    }

    if (gadget.state.lines < count) {
      next_dict.href = url_list[2];
    } else {
      next_dict.class += disabled_suffix;
    }

    // Set the pagination elements
    domsugar(gadget.element.querySelector(':scope > nav'), [
      domsugar('a', first_dict),
      domsugar('a', previous_dict),
      domsugar('a', next_dict),
      domsugar('span', span_dict)
    ]);

    if (scroll_to_last_post) {
      gadget.element.querySelector(':scope > nav').scrollIntoView()
    }
  }

  rJS(window)
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod('getSelectedLanguage', 'getSelectedLanguage')

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function render(options) {
      var gadget = this;

      // Cancel previous line rendering to not conflict with the asynchronous render for now
      gadget.fetchLineContent(true);

      return new RSVP.Queue(RSVP.hash({
        language: gadget.getSelectedLanguage(),
        begin_from: gadget.getUrlParameter(options.key + '_begin_from'),
        last_post: gadget.getUrlParameter('last_post'),
        post_relative_url: gadget.getUrlParameter('post_relative_url')
      }))
        .push(function (result_dict) {
          var begin_from = parseInt(result_dict.begin_from || '0', 10) || 0,
            lines = options.lines || 1;
          if (result_dict.last_post && !isNaN(result_dict.last_post)) {
            var number_of_pages = Math.ceil(result_dict.last_post/lines);
            begin_from = (number_of_pages-1)*lines;
          }
          return gadget.changeState({
            key: options.key,
            language: result_dict.language,
            query_string: Query.objectToSearchText(
              new ComplexQuery({
                operator: "AND",
                type: "complex",
                query_list: Object.entries(options.query_dict)
                                  .map(function (tuple) {
                    return createMultipleSimpleOrQuery(tuple[0], tuple[1]);
                  })
              })
            ),
            begin_from: begin_from,
            lines: lines,
            date_column: options.date_column || 'modification_date',
            sort_order: options.sort_order || 'ASC',
            source_column: options.source_column || 'source_title',
            attachment_column: options.attachment_column || 'Event_getAttachmentList',
            // Force line calculation in any case
            render_timestamp: new Date().getTime(),
            first_render: true,
            allDocs_result: undefined,
            last_post: result_dict.last_post,
            post_relative_url: result_dict.post_relative_url
          });
        });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        allDocs_result,
        first_param,
        prev_param,
        next_param,
        pagination_key;

      if (!gadget.state.query_string) {
        throw new Error('No "query_dict" defined for ' + gadget.state.key);
      }

      if (modification_dict.hasOwnProperty('first_render')) {
        setPaginationElement(gadget, 0, [], modification_dict.hasOwnProperty('last_post'));
      }

      if (modification_dict.hasOwnProperty('render_timestamp')) {
        domsugar(gadget.element.querySelector(':scope > nav > span'), {
          class: "ui-icon-spinner ui-btn-icon-left",
          text: ''
        });
        return gadget.fetchLineContent(false);
      }

      if (modification_dict.hasOwnProperty('allDocs_result')) {
        allDocs_result = JSON.parse(gadget.state.allDocs_result);
        pagination_key = gadget.state.key + '_begin_from';
        first_param = {};
        first_param[pagination_key] = undefined;
        //drop last_post url parameter so pagination links works as usual
        first_param['last_post'] = undefined;
        prev_param = {};
        prev_param[pagination_key] = Math.max(0, gadget.state.begin_from - gadget.state.lines) || undefined;
        prev_param['last_post'] = undefined
        next_param = {};
        next_param[pagination_key] = gadget.state.begin_from + gadget.state.lines;
        next_param['last_post'] = undefined;
        return new RSVP.Queue(RSVP.hash({
          viewer_list: RSVP.all(allDocs_result.data.rows.map(function (entry, i) {
            if (i === gadget.state.lines) {
              return;
            }
            return gadget.declareGadget('gadget_html_viewer.html')
              .push(function (viewer) {
                return viewer.render({value: entry.value.asStrippedHTML})
                  .push(function () {
                    return viewer;
                  });
              });
          })),
          url_list: gadget.getUrlForList([
            {command: 'change', options: first_param},
            {command: 'change', options: prev_param},
            {command: 'change', options: next_param}
          ])
        }))
          .push(function (result_dict) {
            var now = new Date();
            domsugar(gadget.element.querySelector(':scope > ol'),
                     allDocs_result.data.rows.map(function (entry, i) {
                if (i === gadget.state.lines) {
                  // Drop the last lines, in case we reached the +1 post value
                  // from allDocs, used to activate the pagination
                  return '';
                }
                var source_title = entry.value[gadget.state.source_column] || '',
                  attachment_list = entry.value[gadget.state.attachment_column] || [],
                  attachment_element_list = [],
                  j,
                  word_list = source_title.split(' '),
                  source_short_title;

                if (word_list.length === 1) {
                  source_short_title = (word_list[0][0] || '?') + (word_list[0][1] || '');
                } else {
                  source_short_title = word_list[0][0] + word_list[1][0];
                }

                for (j = 0; j < attachment_list.length; j += 1) {
                  attachment_element_list.push(
                    domsugar('li', [
                      domsugar('a', {
                        text: attachment_list[j].title,
                        href: attachment_list[j].url,
                        download: attachment_list[j].title
                      }),
                      ' (',
                      attachment_list[j].content_type || 'application/octet-stream',
                      ')'
                    ])
                  );
                }

                return domsugar('li', [
                  domsugar('div', {
                    class: 'post_avatar',
                    text: source_short_title
                  }),
                  domsugar('div', {
                    class: 'post_content'
                  }, [
                    domsugar('strong', {text: source_title}),
                    " ",
                    domsugar('time', {
                      datetime: entry.value[gadget.state.date_column],
                      title: entry.value[gadget.state.date_column],
                      text: getRelativeTimeString(
                        gadget.state.language,
                        now,
                        new Date(entry.value[gadget.state.date_column])
                      )
                    }),
                    domsugar('br'),
                    result_dict.viewer_list[i].element,
                    domsugar('br'),
                    domsugar('ul', attachment_element_list)
                    // domsugar('hr')
                  ])
                ]);
              }));
            setPaginationElement(gadget, allDocs_result.data.total_rows,
                                 result_dict.url_list,
                                 gadget.state.last_post);
          });
      }
    })

    .onLoop(function () {
      // update relative time
      var now = new Date(),
        gadget = this;
      this.element.querySelectorAll("div.post_content > time").forEach(
        function (element) {
          element.textContent = getRelativeTimeString(
            gadget.state.language,
            now,
            new Date(element.getAttribute('datetime'))
          );
        }
      );
      // Loop every minute
    }, 1000 * 60)

    //////////////////////////////////////////////
    // render the listbox in an asynchronous way
    //////////////////////////////////////////////
    .declareJob('fetchLineContent', function fetchLineContent(only_cancel) {
      if (only_cancel) {
        return;
      }

      var gadget = this,
      limit_options = (gadget.state.lines === 0) ? undefined
        : [gadget.state.begin_from, gadget.state.lines + 1];

      function fetchContent(timeout) {
        return gadget.jio_allDocs({
          query: gadget.state.query_string,
          limit: limit_options,
          select_list: ['asStrippedHTML', gadget.state.date_column,
                        gadget.state.source_column,
                        gadget.state.attachment_column],
          sort_on: [[gadget.state.date_column, gadget.state.sort_order], ['uid', 'ASC']]
        })
        .push(function (result) {
          if (result.data.rows && result.data.rows.length > 0) {
            return gadget.changeState({
              allDocs_result: JSON.stringify(result)
            });
          }
          if (Date.now() > timeout) {
            return gadget.changeState({
              allDocs_result: JSON.stringify(result)
            });
          }
          return new RSVP.Promise(function (resolve) {
            setTimeout(function () {
              resolve(fetchContent(timeout));
            }, 500); // retry every 500ms
          });
        });
      }

      return fetchContent(Date.now() + 5000);
    })

    .declareMethod("getContent", function getContent() {
      return {};
    })

    .declareMethod("checkValidity", function checkValidity() {
      return true;
    });

}(window, rJS, RSVP, console, domsugar, Intl, Query, SimpleQuery,
  ComplexQuery));
