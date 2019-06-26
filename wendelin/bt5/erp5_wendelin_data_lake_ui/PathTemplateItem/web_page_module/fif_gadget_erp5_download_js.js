/*global window, rJS, UriTemplate */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, UriTemplate, document) {
  "use strict";
  function documentation(context, evt) {
    var link = document.createElement('a');
    link.href = window.location.origin + "/erp5/web_site_module/fif_data_runner/#/?page=ebulk_doc";
    link.click();
  }
  function download_linux(context, evt) {
    var link = document.createElement('a');
    link.download = "ebulk.tar.gz";
    link.href = window.location.origin + "/erp5/data_stream_module/embulk_download_script/getData";
    link.click();
  }
  function download_rpm(context, evt) {
    var link = document.createElement('a');
    link.download = "ebulk.rpm";
    link.href = window.location.origin + "/erp5/data_stream_module/embulk_download_rpm/getData";
    link.click();
  }
  function download_win(context, evt) {
    var link = document.createElement('a');
    link.download = "ebulk.zip";
    link.href = window.location.origin + "/erp5/data_stream_module/embulk_download_script_win/getData";
    link.click();
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareJob('documentation', function (evt) {
      return documentation(this, evt);
    })
    .declareJob('download_linux', function (evt) {
      return download_linux(this, evt);
    })
    .declareJob('download_rpm', function (evt) {
      return download_rpm(this, evt);
    })
    .declareJob('download_win', function (evt) {
      return download_win(this, evt);
    })
     .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({page_title: 'Download'});
    })
    .onEvent('submit', function (evt) {
      if (evt.target.name === 'download-linux') {
        return this.download_linux(evt);
      } else if (evt.target.name === 'download-win') {
        return this.download_win(evt);
      } else if (evt.target.name === 'download-rpm') {
        return this.download_rpm(evt);
      } else if (evt.target.name === 'documentation') {
        return this.documentation(evt);
      } else {
        throw new Error('Unknown form');
      }
    });

}(window, rJS, UriTemplate, document));