/*globals window, RSVP, rJS, Handlebars, jIO*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, Handlebars, jIO) {
  "use strict";

  // NO LONGER USED

  // UNSPLASH API
  // API: https://unsplash.com/documentation#creating-a-developer-account
  var CID = "3196c4c1a2915c32bd9ca6ba5a88cec7555e06eb7e580546018f079394e9954f",
    TOKEN = "&amp;client_id=" + CID,

    // UNSPLAH GUIDELINE
    // https://community.unsplash.com/developersblog/unsplash-api-guidelines
    UTM = "?utm_source=AFS&utm_medium=referral&utm_campaign=api-credit",

    gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    source = templater.getElementById("banner-template").innerHTML,
    template = Handlebars.compile(source);

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////

    .ready(function (my_gadget) {
      my_gadget.property_dict = {};
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function () {

      // not much to do, but unsplash would also allow to query for
      // random images, so just search for free + software and
      // display first result

      return new RSVP.Queue()
        .push(function () {
          return jIO.util.ajax({
            type: "GET",
            headers: {"Accept-Version": "v1"},
            url: "https://api.unsplash.com/photos/MTJxRri1UiI" + UTM + TOKEN
          });
        })
        .push(function (my_response) {
          var is_response = my_response.target.response ||
            my_response.target.responseText,
            image_dict;
          if (is_response) {
            image_dict = JSON.parse(is_response);

            //gadget.element.innerHTML =
            // I don't need the gadget hooray, just the container, so sorry.
            return template({
              "message": "What can Free Software do for you?",
              "src": image_dict.urls.full + UTM,
              "alt": "Free Software",
              "source_url": image_dict.user.links.html + UTM,
              "source_title": image_dict.user.name,
              "unsplash_url": "https://unsplash.com/" + UTM
            });
          }
        });
    });

}(window, RSVP, rJS, Handlebars, jIO));
