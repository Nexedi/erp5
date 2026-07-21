/*global window, rJS, RSVP, navigator, PublicKeyCredential */
/*jslint nomen: true, maxlen:200, indent:2*/
(function (window, rJS, RSVP, navigator, PublicKeyCredential) {
  "use strict";

  rJS(window)

    .declareMethod('render', function (options) {
      var public_key_credential_request_json_dict;
      try {
        public_key_credential_request_json_dict = JSON.parse(options.public_key_credential_request_json);
      } catch (error) {
        throw new Error('Can not parse authentication_challenge_json parameters');
      }

      return this.changeState({
        key: options.key,
        editable: (options.editable === undefined) ? true : options.editable,
        public_key_credential_request_json_dict: public_key_credential_request_json_dict,
        challenge: public_key_credential_request_json_dict.challenge
      });
    })

    //////////////////////////////////////////////////
    // Used when submitting the form
    //////////////////////////////////////////////////
    .declareMethod('getContent', function () {
      var gadget = this;
      if (!gadget.state.editable) {
        return {};
      }

      return new RSVP.Queue()
        .push(function () {
          var public_key_credential_request_options = PublicKeyCredential.parseRequestOptionsFromJSON(
            gadget.state.public_key_credential_request_json_dict
          );

          return navigator.credentials.get({
            publicKey: public_key_credential_request_options
          });
        })
        .push(function (public_key_credential) {

          var public_key_credential_json_dict = public_key_credential.toJSON(),
            result = {challenge: gadget.state.challenge};
          result[gadget.state.key] = JSON.stringify(public_key_credential_json_dict);

          return result;
        });

    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      return !!PublicKeyCredential;
    }, {mutex: 'changestate'});

}(window, rJS, RSVP, navigator, PublicKeyCredential));