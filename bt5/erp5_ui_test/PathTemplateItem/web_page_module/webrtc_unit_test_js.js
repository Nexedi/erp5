/*global window, document, rJS, JSON, QUnit, jQuery, RSVP, console, setTimeout*/

(function(rJS, QUnit, RSVP, $) {
  "use strict";
  var error_handler = function(e) {
      window.console.error(e);
      ok(false, e);
    },
    connection_options = [
      {
        // No need for stun server on the same lan / ipv6
        iceServers: [
                  {'url': 'stun:23.21.150.121'},
                  {url: 'stun:stun.1.google.com:19302'}
          ]
      },
      {
        'optional': [{DtlsSrtpKeyAgreement: true}]
      }
    ],
    data_channel_options = {reliable: true},
    offer_contraints = {
      mandatory: {
        OfferToReceiveAudio: false,
        OfferToReceiveVideo: false
      }
    },
    offer = {"type":"offer", "sdp":"v=0\r\n\
o=- 2708361213080913936 2 IN IP4 127.0.0.1\r\n\
s=-\r\n\
t=0 0\r\n\
a=msid-semantic: WMS\r\n\
m=application 60581 DTLS/SCTP 5000\r\n\
c=IN IP4 82.226.112.70\r\n\
a=candidate:3097449529 1 udp 2113937151 192.168.242.146 60581 typ host generation 0 network-cost 50\r\n\
a=candidate:421107265 1 udp 2113939711 2a01:e35:2e27:460:3430:1418:c2a6:f8e5 43111 typ host generation 0 network-cost 50\r\n\
a=candidate:842163049 1 udp 1677729535 82.226.112.70 60581 typ srflx raddr 192.168.242.146 rport 60581 generation 0 network-cost 50\r\n\
a=ice-ufrag:N0ey\r\n\
a=ice-pwd:hgfceTKEWpBojQfb+iA3DG0x\r\n\
a=fingerprint:sha-256 56:82:C4:19:56:BA:BE:B2:37:E0:9B:87:44:AB:0C:D1:7A:4C:61:E1:AA:1D:56:70:91:EE:7D:1E:57:BC:28:3A\r\n\
a=setup:actpass\r\n\
a=mid:data\r\n\
a=sctpmap:5000 webrtc-datachannel 1024\r\n"
}    

  QUnit.config.testTimeout = 60000;
  rJS(window)
    .ready(function(g) {
      g.props = {};
      g.props.Alice = {},
      g.props.Bob = {},
      g.props.config = {
        type: "query",
        sub_storage : {
          type: "uuid",
          sub_storage: {
            "type":     "indexeddb",
            "database": "serverless"
          }
        }
      };

      g.props.description_defer = new RSVP.defer();
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .allowPublicAcquisition("notifyDescriptionCalculated", function (args) {
      this.props.description_defer.resolve(args[0]);
      this.props.description_defer = RSVP.defer();
    })
    .declareService(function() {
      var g = this;
      QUnit.test("Initiate Clients", function( assert ) {
        assert.expect(2);
        var done = assert.async();
        return g.getDeclaredGadget("alice_handshake_gadget")
        .then(function(new_gadget) {
          g.props.Alice.alice_handshake_gadget = new_gadget;
          return g.props.Alice.alice_handshake_gadget.register("meetup", "alice", g.props.config);
        })
        .then(function(res) {
          assert.equal(res[0], "meetup_alice", "Alice initiate the handshake gadget and register");
          return g.getDeclaredGadget("bob_handshake_gadget")
        })
        .then(function(new_gadget) {
          g.props.Bob.bob_handshake_gadget = new_gadget;
          return g.props.Bob.bob_handshake_gadget.register("meetup", "bob", g.props.config);
        })
        .then(function(res) {
          assert.equal(res[0], "meetup_bob", "Bob initiate the handshake gadget and register");
        })
        .then(function(new_gadget) {
          var new_element = document.createElement("div");
          g.props.element.querySelector(".gadget_webrtc").appendChild(new_element);
          var scope = "webrtc_bob";
          return g.declareGadget("gadget_webrtc.html", {
            scope: scope,
            element: new_element
          })
        })
        .then(function(rtc_gadget) {
          g.props.Bob.webrtc_gadget = rtc_gadget;
        })
        .then(function(new_gadget) {
          var new_element = document.createElement("div");
          g.props.element.querySelector(".gadget_webrtc").appendChild(new_element);
          var scope = "webrtc_alice";
          return g.declareGadget("gadget_webrtc.html", {
            scope: scope,
            element: new_element
          })
        })
        .then(function(rtc_gadget) {
          g.props.Alice.webrtc_gadget = rtc_gadget;
        })
        .fail(error_handler).always(done);
      });
      
      QUnit.test("Alice waits and picks the Offer as available", function( assert ) {
          var done = assert.async();
          assert.expect(1);
          var offer_deffer = RSVP.defer();
          return g.props.Alice.alice_handshake_gadget.wait_until_available("meetup", "alice_",
              function(response){
                assert.equal(JSON.parse(response[0]).from, "bob", "Alice waits for the offer while other tests are running and picks the offer from bob as offer gets available.");
                offer_deffer.resolve();
          })
          .fail(error_handler).always(done);
      });

      QUnit.test("Bob can create offer", function( assert ) {
        var local_description;
        var done = assert.async();
        assert.expect(4);
        return new RSVP.Queue()
        .then(function() {
          return g.props.Bob.webrtc_gadget.createConnection.apply(g.props.Bob.webrtc_gadget, connection_options)
          .push(function () {
            return g.props.Bob.webrtc_gadget.createDataChannel("bob", data_channel_options);
          })
          .push(function () {
            return g.props.Bob.webrtc_gadget.createOffer(offer_contraints);
          })
          .push(function (ld) {
            local_description = ld;
            assert.equal(local_description.type, "offer", "Check if local driscription genrated is of type offer");
            return g.props.Bob.webrtc_gadget.setLocalDescription(local_description);
          })
          .push(function () {
            return g.props.description_defer.promise;
          });
        })
        .then(function(description) {
          // diff to check ice candidates
          var parsed_desc = JSON.parse(description),
            count = 0,
            i;

          assert.notDeepEqual(parsed_desc.sdp, local_description, "Diff the local driscription generated above with the ice candidates ");

          var line_list = parsed_desc.sdp.split('\n');
          for (i = 0; i < line_list.length; i += 1) {
            if (line_list[i].indexOf('a=candidate:') === 0) {
              count += 1;
            }
          }
          assert.equal(count, 3, "Check if all the 3 ice candidates are generated sucessfully");
          assert.equal(parsed_desc.type, "offer", "Check if final type is offer");
        })
        .fail(error_handler).always(done);
      });

      QUnit.test("Bob can send Offer", function( assert ) {
          var done = assert.async();
          assert.expect(2);
         
          var params = {'name': 'alice_bob',
                        'data' : new Blob([JSON.stringify({from: 'bob', 
                                                           action: "offer", 
                                                          data: offer})], 
                                              {type : "application/json"})};

          return g.props.Bob.bob_handshake_gadget.handle_offer_answer("meetup", params)
          .then(function(res) {
            assert.equal(res[0], "meetup_alice_bob", "Check if Bob sucessfully saves the offer into the JIO ");
            return g.props.Bob.bob_handshake_gadget.get_answer('meetup', "alice_bob");
          })
          .then(function(res) {
            assert.deepEqual(res, params.data, "Check if the data retrived is same as data entered");
          })
          .fail(error_handler).always(done);
      });

      QUnit.test("Alice generates an answer", function( assert ) {
        var done = assert.async();

        assert.expect(2);
        
        var webrtc = g.props.Alice.webrtc_gadget;
        return webrtc.createConnection.apply(webrtc, connection_options)
        .push(function () {
          return webrtc.setRemoteDescription(JSON.stringify(offer));
        })
        .push(function () {
          return webrtc.createAnswer(offer_contraints);
        })
        .push(function (local_description) {
          return webrtc.setLocalDescription(local_description);
        })
        .push(function () {
          g.props.description_defer = new RSVP.defer();
          return g.props.description_defer.promise;
        })
        .then(function(res) {
          var parsed_desc = JSON.parse(res),
            count = 0;
          var line_list = parsed_desc.sdp.split('\n');
          for (var i = 0; i < line_list.length; i += 1) {
            if (line_list[i].indexOf('a=candidate:') === 0) {
              count += 1;
            }
          }
          assert.equal(count, 3, "Check if all the 3 ice candidates are generated sucessfully");
          assert.equal(parsed_desc.type, "answer", "Check if genrated description is of type answer");
        })
        .fail(error_handler).always(done);
      });
    });
})(rJS, QUnit, RSVP, jQuery);