/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global rJS, RSVP, window, navigator*/
(function (rJS, RSVP, window, navigator) {
  "use strict";

  var COPY_LABEL = "Copy to Clipboard",
    COPIED_LABEL = "Copied",
    GENERATE_LABEL = "Get RSS access link",
    LOADING_LABEL = "Loading RSS link...",
    ERROR_LABEL = "Fail to load RSS link. Please try again later.",
    LABEL_LIST = [COPY_LABEL, COPIED_LABEL, GENERATE_LABEL, LOADING_LABEL,
                  ERROR_LABEL],
    BUTTON_CLASS = "ui-btn-icon-left",
    RSS_URL_SCRIPT = "DiscussionForum_getRssAccessUrlAsJSON";

  function getTranslationDict(gadget) {
    return gadget.getTranslationList(LABEL_LIST)
      .push(function (translation_list) {
        var i,
          translation_dict = {};
        for (i = 0; i < LABEL_LIST.length; i += 1) {
          translation_dict[LABEL_LIST[i]] = translation_list[i];
        }
        return translation_dict;
      });
  }

  function generateRssUrl(gadget) {
    return gadget.changeState({status: LOADING_LABEL})
      .push(function () {
        return gadget.getSetting("hateoas_url");
      })
      .push(function (hateoas_url) {
        return gadget.jio_getAttachment(
          "erp5",
          hateoas_url + gadget.state.jio_key + "/" + RSS_URL_SCRIPT,
          {format: "json"}
        );
      })
      .push(function (result) {
        return gadget.changeState({status: "", rss_url: result.rss_url});
      }, function (error) {
        return gadget.changeState({status: ERROR_LABEL})
          .push(function () {
            throw error;
          });
      });
  }

  function copyRssUrl(gadget) {
    return new RSVP.Queue()
      .push(function () {
        return navigator.clipboard.writeText(gadget.state.rss_url);
      })
      .push(function () {
        return gadget.notifyChange({
          "message": gadget.state.translation_dict[COPIED_LABEL],
          "status": "success"
        });
      });
  }

  rJS(window)
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod('render', function (options) {
      var gadget = this;
      return getTranslationDict(gadget)
        .push(function (translation_dict) {
          return gadget.changeState({
            rss_url: options.rss_url || "",
            jio_key: options.jio_key || "",
            status: "",
            translation_dict: translation_dict
          });
        });
    })

    .onStateChange(function () {
      var gadget = this,
        translation_dict = gadget.state.translation_dict,
        button = gadget.element.querySelector('button'),
        field_element = gadget.element.querySelector('div');

      if (gadget.state.status) {
        button.textContent = translation_dict[gadget.state.status];
        return;
      }
      if (!gadget.state.rss_url) {
        field_element.hidden = true;
        button.className = BUTTON_CLASS + " ui-icon-rss";
        button.textContent = translation_dict[GENERATE_LABEL];
        return;
      }
      field_element.hidden = false;
      button.className = BUTTON_CLASS + " ui-icon-copy";
      button.textContent = translation_dict[COPY_LABEL];
      return gadget.getDeclaredGadget('text_field')
        .push(function (text_gadget) {
          return text_gadget.render({
            value: gadget.state.rss_url
          });
        });
    })

    .onEvent('click', function (evt) {
      var gadget = this;

      if (evt.target.tagName !== 'BUTTON') {
        return;
      }
      evt.preventDefault();

      if (gadget.state.status === LOADING_LABEL) {
        return;
      }
      if (gadget.state.rss_url) {
        return copyRssUrl(gadget);
      }
      return generateRssUrl(gadget);
    }, false, false);

}(rJS, RSVP, window, navigator));