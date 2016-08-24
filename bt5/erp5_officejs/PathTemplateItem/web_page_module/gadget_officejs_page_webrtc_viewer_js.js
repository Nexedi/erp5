/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  function getMaxHeight(wrap_obj) {
    var height;
    if (wrap_obj) {
      height = window.innerHeight - wrap_obj.offsetTop;
    } else {
      height = window.innerHeight;
    }
    if (height < 400) {
      height = 400;
    }
    return height + "px";
  }

  function setFillStyle(gadget) {
    var iframe = gadget.props.element.querySelector('iframe'),
      height = getMaxHeight(iframe),
      width = "100%";
    iframe.setAttribute(
      'style',
      'width: ' + width + '; border: 2px solid; height: ' + height
    );
    return {height: height, width: width};
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
          g.props.content = '';
        });
    })
    
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .allowPublicAcquisition("notifyDataChannelMessage", function (argument_list, scope) {
      var data = JSON.parse(argument_list[0]);
      if (data.extra_props) {
        this.props.element.querySelector("#extra").innerHTML = data.extra_props;
        $('#extra').find('[data-role=collapsible]').collapsible({ enhanced: true });
      }
      if (data.title) {
        this.props.element.querySelector(".viewer-content").firstChild.contentDocument.body.innerHTML = data.content;
        this.props.element.querySelector(".ui-field-contain").childNodes[3].firstChild.value = data.title;
        this.props.title = data.title;
      }

      this.props.content = data.content;
      
    })
    
    .allowPublicAcquisition('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })

    .declareMethod('triggerSubmit', function () {
      return this.props.element.querySelector('button').click();
    })    

    .declareMethod("render", function(options) {
      var gadget = this;
      gadget.props.options = options;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            title: "Document Viewer",
            refresh_action: true
          });
        });
    })

    .declareService(function () {
      var gadget = this;
      if(window.location.hash) {
        var room = gadget.props.options["room"];
        return gadget.notifySubmitting()
        .push(function() {
          return gadget.getDeclaredGadget('share_text_via_webrtc')
        })
        .push(function(g){
          if(gadget.props.options['config']) {
            return g.slaveInitiate(room, gadget, gadget.props.options['config']);
          } else {
            return g.slaveInitiate(room, gadget)
            .push(null, function(error){
              return gadget.notifySubmitted()
                .push(function () {
                  throw error;
                });
            });
          }
        })
        .push(function(){
          return gadget.notifySubmitted();
        });
      }
    })
    
    .declareService(function() {
      var gadget = this;
      var iframe = document.createElement("iframe");
      gadget.props.element.querySelector(".viewer-content").appendChild(iframe);
      return setFillStyle(gadget);
    })
    
    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('form'),
            'submit',
            true,
            function (event) {
              gadget.props.element.querySelector(".viewer-content").firstChild.contentDocument.body.innerHTML = gadget.props.content;
            }
          );
        });
    });
}(window, RSVP, rJS));