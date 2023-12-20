/*jslint indent: 2, nomen: true */
/*global window, rJS, RSVP, PDFViewerApplication, PDFViewerApplicationOptions, FileReader */
(function (window, rJS, RSVP, PDFViewerApplication, PDFViewerApplicationOptions) {
  "use strict";

  function getViewerConfiguration() {
    return {
      appContainer: document.body,
      mainContainer: document.getElementById("viewerContainer"),
      viewerContainer: document.getElementById("viewer"),
      toolbar: {
        container: document.getElementById("toolbarViewer"),
        numPages: document.getElementById("numPages"),
        pageNumber: document.getElementById("pageNumber"),
        scaleSelect: document.getElementById("scaleSelect"),
        customScaleOption: document.getElementById("customScaleOption"),
        previous: document.getElementById("previous"),
        next: document.getElementById("next"),
        zoomIn: document.getElementById("zoomIn"),
        zoomOut: document.getElementById("zoomOut"),
        viewFind: document.getElementById("viewFind"),
        openFile: document.getElementById("openFile"),
        print: document.getElementById("print"),
        editorFreeTextButton: document.getElementById("editorFreeText"),
        editorFreeTextParamsToolbar: document.getElementById("editorFreeTextParamsToolbar"),
        editorInkButton: document.getElementById("editorInk"),
        editorInkParamsToolbar: document.getElementById("editorInkParamsToolbar"),
        editorStampButton: document.getElementById("editorStamp"),
        editorStampParamsToolbar: document.getElementById("editorStampParamsToolbar"),
        download: document.getElementById("download")
      },
      secondaryToolbar: {
        toolbar: document.getElementById("secondaryToolbar"),
        toggleButton: document.getElementById("secondaryToolbarToggle"),
        presentationModeButton: document.getElementById("presentationMode"),
        openFileButton: document.getElementById("secondaryOpenFile"),
        printButton: document.getElementById("secondaryPrint"),
        downloadButton: document.getElementById("secondaryDownload"),
        viewBookmarkButton: document.getElementById("viewBookmark"),
        firstPageButton: document.getElementById("firstPage"),
        lastPageButton: document.getElementById("lastPage"),
        pageRotateCwButton: document.getElementById("pageRotateCw"),
        pageRotateCcwButton: document.getElementById("pageRotateCcw"),
        cursorSelectToolButton: document.getElementById("cursorSelectTool"),
        cursorHandToolButton: document.getElementById("cursorHandTool"),
        scrollPageButton: document.getElementById("scrollPage"),
        scrollVerticalButton: document.getElementById("scrollVertical"),
        scrollHorizontalButton: document.getElementById("scrollHorizontal"),
        scrollWrappedButton: document.getElementById("scrollWrapped"),
        spreadNoneButton: document.getElementById("spreadNone"),
        spreadOddButton: document.getElementById("spreadOdd"),
        spreadEvenButton: document.getElementById("spreadEven"),
        documentPropertiesButton: document.getElementById("documentProperties")
      },
      sidebar: {
        outerContainer: document.getElementById("outerContainer"),
        sidebarContainer: document.getElementById("sidebarContainer"),
        toggleButton: document.getElementById("sidebarToggle"),
        resizer: document.getElementById("sidebarResizer"),
        thumbnailButton: document.getElementById("viewThumbnail"),
        outlineButton: document.getElementById("viewOutline"),
        attachmentsButton: document.getElementById("viewAttachments"),
        layersButton: document.getElementById("viewLayers"),
        thumbnailView: document.getElementById("thumbnailView"),
        outlineView: document.getElementById("outlineView"),
        attachmentsView: document.getElementById("attachmentsView"),
        layersView: document.getElementById("layersView"),
        outlineOptionsContainer: document.getElementById("outlineOptionsContainer"),
        currentOutlineItemButton: document.getElementById("currentOutlineItem")
      },
      findBar: {
        bar: document.getElementById("findbar"),
        toggleButton: document.getElementById("viewFind"),
        findField: document.getElementById("findInput"),
        highlightAllCheckbox: document.getElementById("findHighlightAll"),
        caseSensitiveCheckbox: document.getElementById("findMatchCase"),
        matchDiacriticsCheckbox: document.getElementById("findMatchDiacritics"),
        entireWordCheckbox: document.getElementById("findEntireWord"),
        findMsg: document.getElementById("findMsg"),
        findResultsCount: document.getElementById("findResultsCount"),
        findPreviousButton: document.getElementById("findPrevious"),
        findNextButton: document.getElementById("findNext")
      },
      passwordOverlay: {
        dialog: document.getElementById("passwordDialog"),
        label: document.getElementById("passwordText"),
        input: document.getElementById("password"),
        submitButton: document.getElementById("passwordSubmit"),
        cancelButton: document.getElementById("passwordCancel")
      },
      documentProperties: {
        dialog: document.getElementById("documentPropertiesDialog"),
        closeButton: document.getElementById("documentPropertiesClose"),
        fields: {
          fileName: document.getElementById("fileNameField"),
          fileSize: document.getElementById("fileSizeField"),
          title: document.getElementById("titleField"),
          author: document.getElementById("authorField"),
          subject: document.getElementById("subjectField"),
          keywords: document.getElementById("keywordsField"),
          creationDate: document.getElementById("creationDateField"),
          modificationDate: document.getElementById("modificationDateField"),
          creator: document.getElementById("creatorField"),
          producer: document.getElementById("producerField"),
          version: document.getElementById("versionField"),
          pageCount: document.getElementById("pageCountField"),
          pageSize: document.getElementById("pageSizeField"),
          linearized: document.getElementById("linearizedField")
        }
      },
      altTextDialog: {
        dialog: document.getElementById("altTextDialog"),
        optionDescription: document.getElementById("descriptionButton"),
        optionDecorative: document.getElementById("decorativeButton"),
        textarea: document.getElementById("descriptionTextarea"),
        cancelButton: document.getElementById("altTextCancel"),
        saveButton: document.getElementById("altTextSave")
      },
      annotationEditorParams: {
        editorFreeTextFontSize: document.getElementById("editorFreeTextFontSize"),
        editorFreeTextColor: document.getElementById("editorFreeTextColor"),
        editorInkColor: document.getElementById("editorInkColor"),
        editorInkThickness: document.getElementById("editorInkThickness"),
        editorInkOpacity: document.getElementById("editorInkOpacity"),
        editorStampAddImage: document.getElementById("editorStampAddImage")
      },
      printContainer: document.getElementById("printContainer"),
      openFileInput: document.getElementById("fileInput"),
      debuggerScriptPath: "./debugger.js"
    };
  };

  rJS(window)
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.props.element = element;
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.props.key = options.key;
      var config = getViewerConfiguration();
      PDFViewerApplicationOptions.set("disablePreferences", true);
      PDFViewerApplicationOptions.set("locale", options.language);
      PDFViewerApplicationOptions.set("workerSrc", "./pdf_js/build/pdf.worker.js");

      return PDFViewerApplication.initialize(config).then(function() {
        if (options.password) {
          PDFViewerApplication.passwordPrompt._original_open = PDFViewerApplication.passwordPrompt.open;
          var retries = 0;
          PDFViewerApplication.passwordPrompt.open = function () {
            if (retries) {
              return this._original_open();
            }
            return new Promise((resolve) => {
              this.input.value = options.password;
              this.submitButton.dispatchEvent(new Event("click"));
              retries++;
              resolve();
            }).then(() => {
              PDFViewerApplication.passwordPrompt.close();
            });
          };
        }
      }).then(function() { 
        return PDFViewerApplication.open({url: options.value})
          .catch(function(e){
            if (e.name == "InvalidPDFException" || e.name == "PasswordException") {
              const dialog = document.createElement("dialog");
              dialog.textContent = e.message;
              document.getElementById("dialogContainer").append(dialog);
              dialog.showModal();
              return;
            }
            throw e;
          })
      })
    })
    .declareMethod("getContent", function () {
      var form_data = {};
      var self = this;
      return new RSVP.Queue()
      .push(function () {
        if (PDFViewerApplication.pdfDocument) {
          return PDFViewerApplication.pdfDocument.saveDocument();
        }
      })
      .push(function (data) {
        var blob = new Blob([data], {"type": "application/pdf"});
        var filereader = new FileReader();
        return new RSVP.Promise(function (resolve, reject, notify) {
          filereader.addEventListener("load", resolve);
          filereader.addEventListener("error", reject);
          filereader.addEventListener("progress", notify);
          filereader.readAsDataURL(blob);
        }, function () {
          filereader.abort();
        });
      })
      .push(function (evt) {
        form_data[self.props.key] = evt.target.result;
        return form_data;
      });
    });
}(window, rJS, RSVP, PDFViewerApplication, PDFViewerApplicationOptions));
