"use strict";

AscCommon.readBlobAsDataURL = function (blob) {
  var fr = new FileReader();
  return new RSVP.Promise(function (resolve, reject, notify) {
    fr.addEventListener("load", function () {
      resolve(fr.result);
    });
    fr.addEventListener("error", reject);
    fr.addEventListener("progress", notify);
    fr.readAsDataURL(blob);
  }, function () {
    fr.abort();
  });
};

AscCommon.downloadUrlAsBlob = function (url) {
  var xhr = new XMLHttpRequest();
  return new RSVP.Promise(function (resolve, reject) {
    xhr.open("GET", url);
    xhr.responseType = "blob";//force the HTTP response, response-type header to be blob
    xhr.onload = function () {
      if (this.status === 200) {
        resolve(xhr.response);
      } else {
        reject(this.status);
      }
    };
    xhr.onerror = reject;
    xhr.send();
  }, function () {
    xhr.abort();
  });
};

AscCommon.baseEditorsApi.prototype.jio_open = function () {
  var t = this,
    g = Common.Gateway;
  g.jio_getAttachment('/', 'body.txt')
    .push(undefined, function (error) {
      if (error.status_code === 404) {
        return g.props.value;
      }
      throw error;
    })
    .push(function (doc) {
      if (!doc) {
        switch (g.props.documentType) {
          case "presentation":
            doc = t.getEmpty();
            break;
          case "spreadsheet":
            doc = "XLSY;v2;2286;BAKAAgAAA+cHAAAEAwgAAADqCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGMFAAAAEQAAAAEMAAAABwEAAAAACAEAAAAABAoAAAAFAAAAAAUAAAAABnwAAAAHGgAAAAQGCgAAAEEAcgBpAGEAbAAGBQAAAAAAACRABxoAAAAEBgoAAABBAHIAaQBhAGwABgUAAAAAAAAkQAcaAAAABAYKAAAAQQByAGkAYQBsAAYFAAAAAAAAJEAHGgAAAAQGCgAAAEEAcgBpAGEAbAAGBQAAAAAAACRACB8AAAAJGgAAAAAGDgAAAEcARQBOAEUAUgBBAEwAAQSkAAAADhYDAAADPwAAAAABAQEBAQMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEpAAAAA0GGAAAAAABBAEEAAAAAAUBAAYEAAAAAAcBAAgBAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAEAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAgAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQCAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAQAAAAkEKwAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQpAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAEAAAAJBCwAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAQAAAAkEKgAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQJAAAAAkoAAAADRQAAAAABAAEBAAMBAAYEAAAAAAcEAAAAAAgEAAAAAAkEpAAAAAwEAAAAAA0GGAAAAAABBAEEAAAAAAUBAAYEAAAAAAcBAAgBAA8qAQAAECkAAAAABAAAAAAAAAABAQAAAAAEDAAAAE4AbwByAG0AYQBsAAUEAAAAAAAAABAnAAAAAAQAAAADAAAAAQEAAAAABAoAAABDAG8AbQBtAGEABQQAAAAPAAAAEC8AAAAABAAAAAYAAAABAQAAAAAEEgAAAEMAbwBtAG0AYQAgAFsAMABdAAUEAAAAEAAAABAtAAAAAAQAAAAEAAAAAQEAAAAABBAAAABDAHUAcgByAGUAbgBjAHkABQQAAAARAAAAEDUAAAAABAAAAAcAAAABAQAAAAAEGAAAAEMAdQByAHIAZQBuAGMAeQAgAFsAMABdAAUEAAAAEgAAABArAAAAAAQAAAAFAAAAAQEAAAAABA4AAABQAGUAcgBjAGUAbgB0AAUEAAAAEwAAABgAAAAAAwAAAAEBAAELAAAAAgYAAAAABAAAAADjAAAAAN4AAAABGwAAAAAGDAAAAFMAaABlAGUAdAAxAAEEAQAAAAIBAgIkAAAAAx8AAAABAQACBAEEAAADBAEAAAAEBAAAAAAFBXnalahdiStABAQAAABBADEAFhEAAAAXDAAAAAQBAAAAAQYBAAAAAQsKAAAAAQWamZmZmZkpQA48AAAAAAVxPQrXowA0QAEFKFyPwvUIOkACBXE9CtejADRAAwUoXI/C9Qg6QAQFcT0K16MANEAFBXE9CtejADRADwYAAAAAAQEBAQkQBgAAAAABAQEBAAkAAAAAGAYAAAACAQAAAAAAAAAA";
            break;
          case "text":
            doc = window.g_sEmpty_bin;
            break;
        }
      }
      t._OfflineAppDocumentEndLoad('', doc);
    })
    .push(undefined, function (error) {
      console.log(error);
    });
};

AscCommon.baseEditorsApi.prototype.jio_save = function () {
  var t = this,
    g = Common.Gateway,
    result = {},
    data = t.asc_nativeGetFile();
  if (g.props.save_defer) {
    // if we are run from getContent
    result[g.props.key] = data;
    g.props.save_defer.resolve(result);
    g.props.save_defer = null;
  } else {
    // TODO: rewrite to put_attachment
    return g.jio_putAttachment('/', 'body.txt', data)
      .push(undefined, function (error) {
        console.log(error);
      });
  }
};

AscCommon.loadSdk = function (sdkName, callback) {
  var queue,
    list_files;
  function loadScript(src) {
    return new RSVP.Promise(function (resolve, reject) {
      var s;
      s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  if (window.AscNotLoadAllScript) {
    callback();
  } else {
    queue = new RSVP.Queue();

    switch (sdkName) {
      case 'word':
        list_files = [
          "../common/downloaderfiles.js",
          "../common/NumFormat.js",
          "../common/SerializeChart.js",

          "../common/FontsFreeType/font_engine.js",
          "../common/FontsFreeType/FontFile.js",
          "../common/FontsFreeType/font_map.js",
          "../common/FontsFreeType/FontManager.js",
          "../word/Editor/FontClassification.js",

          "../common/Drawings/Metafile.js",
          "../common/FontsFreeType/TextMeasurer.js",
          "../common/Drawings/WorkEvents.js",

          "../word/Editor/History.js",

          "../common/Shapes/EditorSettings.js",
          "../common/Shapes/Serialize.js",
          "../common/Shapes/SerializeWriter.js",

          "../common/Drawings/Hit.js",
          "../common/Drawings/ArcTo.js",
          "../common/Drawings/ColorArray.js",

          "../common/Drawings/CommonController.js",
          "../word/Editor/GraphicObjects/DrawingStates.js",
          "../common/Drawings/DrawingsChanges.js",
          "../common/Drawings/Format/CreateGeometry.js",
          "../common/Drawings/Format/Geometry.js",
          "../common/Drawings/Format/Format.js",
          "../common/Drawings/Format/GraphicObjectBase.js",
          "../common/Drawings/Format/Shape.js",
          "../common/Drawings/Format/Path.js",
          "../common/Drawings/Format/Image.js",
          "../common/Drawings/Format/GroupShape.js",
          "../common/Drawings/Format/ChartSpace.js",
          "../common/Drawings/Format/ChartFormat.js",
          "../common/Drawings/Format/TextBody.js",
          "../common/Drawings/Format/GraphicFrame.js",
          "../common/Charts/charts.js",
          "../common/Charts/DrawingArea.js",
          "../common/Charts/DrawingObjects.js",
          "../common/Charts/3DTransformation.js",
          "../common/Charts/ChartsDrawer.js",
          "../common/Drawings/TrackObjects/AdjustmentTracks.js",
          "../common/Drawings/TrackObjects/MoveTracks.js",
          "../common/Drawings/TrackObjects/NewShapeTracks.js",
          "../common/Drawings/TrackObjects/PolyLine.js",
          "../common/Drawings/TrackObjects/ResizeTracks.js",
          "../common/Drawings/TrackObjects/RotateTracks.js",
          "../common/Drawings/TrackObjects/Spline.js",
          "../common/Drawings/DrawingObjectsHandlers.js",
          "../common/Drawings/TextDrawer.js",

          "../common/Drawings/Externals.js",
          "../common/GlobalLoaders.js",
          "../common/Controls.js",
          "../common/Overlay.js",
          "../common/Drawings/HatchPattern.js",

          "../common/scroll.js",
          "../common/Scrolls/iscroll.js",
          "../common/Scrolls/mobileTouchManagerBase.js",
          "../word/Drawing/mobileTouchManager.js",

          "../common/wordcopypaste.js",

          "../cell/utils/utils.js",
          "../cell/model/WorkbookElems.js",
          "../cell/model/Workbook.js",
          "../cell/model/Serialize.js",
          "../cell/model/CellInfo.js",

          "../word/Drawing/translations.js",
          "../word/Editor/GraphicObjects/Format/ShapePrototype.js",
          "../word/Editor/GraphicObjects/Format/ImagePrototype.js",
          "../word/Editor/GraphicObjects/Format/GroupPrototype.js",
          "../word/Editor/GraphicObjects/Format/ChartSpacePrototype.js",
          "../word/Editor/GraphicObjects/GraphicObjects.js",
          "../word/Editor/GraphicObjects/GraphicPage.js",
          "../word/Editor/GraphicObjects/WrapManager.js",
          "../word/Editor/Comments.js",
          "../word/Editor/CommentsChanges.js",
          "../word/Editor/Styles.js",
          "../word/Editor/StylesChanges.js",
          "../word/Editor/FlowObjects.js",
          "../word/Editor/ParagraphContent.js",
          "../word/Editor/ParagraphContentBase.js",
          "../word/Editor/Paragraph/ParaTextPr.js",
          "../word/Editor/Paragraph/ParaTextPrChanges.js",
          "../word/Editor/Paragraph/ParaDrawing.js",
          "../word/Editor/Paragraph/ParaDrawingChanges.js",
          "../word/Editor/Hyperlink.js",
          "../word/Editor/HyperlinkChanges.js",
          "../word/Editor/Field.js",
          "../word/Editor/FieldChanges.js",
          "../word/Editor/Run.js",
          "../word/Editor/RunChanges.js",
          "../word/Editor/Math.js",
          "../word/Editor/MathChanges.js",
          "../word/Editor/Paragraph.js",
          "../word/Editor/ParagraphChanges.js",
          "../word/Editor/Paragraph_Recalculate.js",
          "../word/Editor/Sections.js",
          "../word/Editor/SectionsChanges.js",
          "../word/Editor/Numbering.js",
          "../word/Editor/NumberingChanges.js",
          "../word/Editor/HeaderFooter.js",
          "../word/Editor/DocumentContentBase.js",
          "../word/Editor/Document.js",
          "../word/Editor/DocumentChanges.js",
          "../word/Editor/DocumentContent.js",
          "../word/Editor/DocumentContentChanges.js",
          "../word/Editor/DocumentControllerBase.js",
          "../word/Editor/LogicDocumentController.js",
          "../word/Editor/DrawingsController.js",
          "../word/Editor/HeaderFooterController.js",
          "../word/Editor/Common.js",
          "../word/Editor/Table.js",
          "../word/Editor/Table/TableChanges.js",
          "../word/Editor/Table/TableRecalculate.js",
          "../word/Editor/Table/TableDraw.js",
          "../word/Editor/Table/TableRow.js",
          "../word/Editor/Table/TableRowChanges.js",
          "../word/Editor/Table/TableCell.js",
          "../word/Editor/Table/TableCellChanges.js",
          "../word/Editor/Serialize2.js",
          "../word/Editor/Search.js",
          "../word/Editor/Spelling.js",
          "../word/Editor/Footnotes.js",
          "../word/Editor/FootnotesChanges.js",
          "../word/Editor/FootEndNote.js",

          "../word/Drawing/Graphics.js",
          "../word/Drawing/ShapeDrawer.js",

          "../word/Drawing/DrawingDocument.js",
          "../word/Drawing/GraphicsEvents.js",
          "../word/Drawing/Rulers.js",
          "../word/Drawing/HtmlPage.js",
          "../word/Drawing/documentrenderer.js",
          "../word/document/empty.js",
          "../word/Math/mathTypes.js",
          "../word/Math/mathText.js",
          "../word/Math/mathContent.js",
          "../word/Math/base.js",
          "../word/Math/fraction.js",
          "../word/Math/degree.js",
          "../word/Math/matrix.js",
          "../word/Math/limit.js",
          "../word/Math/nary.js",
          "../word/Math/radical.js",
          "../word/Math/operators.js",
          "../word/Math/accent.js",
          "../word/Math/borderBox.js",

          "../word/apiBuilder.js",

          "../common/clipboard_base.js",
          "../common/text_input.js",
          "../common/Drawings/Format/OleObject.js",
          "../common/Drawings/Format/DrawingContent.js",
          "../common/plugins.js",
          "../common/Local/common_jio.js",
          "../word/Local/api_jio.js"
        ];
        break;
      case 'cell':
        list_files = [
          "../common/downloaderfiles.js",
          "../common/NumFormat.js",
          "../common/SerializeChart.js",

          "../common/FontsFreeType/font_engine.js",
          "../common/FontsFreeType/FontFile.js",
          "../common/FontsFreeType/font_map.js",
          "../common/FontsFreeType/FontManager.js",
          "../word/Editor/FontClassification.js",

          "../common/Drawings/Metafile.js",
          "../common/FontsFreeType/TextMeasurer.js",
          "../common/Drawings/WorkEvents.js",

          "../cell/model/History.js",

          "../common/Shapes/EditorSettings.js",
          "../common/Shapes/Serialize.js",
          "../common/Shapes/SerializeWriter.js",

          "../common/Drawings/Hit.js",
          "../common/Drawings/ArcTo.js",
          "../common/Drawings/ColorArray.js",

          "../common/Drawings/CommonController.js",
          "../common/Drawings/States.js",
          "../common/Drawings/Format/CreateGeometry.js",
          "../common/Drawings/DrawingsChanges.js",
          "../common/Drawings/Format/Geometry.js",
          "../common/Drawings/Format/Format.js",
          "../common/Drawings/Format/GraphicObjectBase.js",
          "../common/Drawings/Format/Shape.js",
          "../common/Drawings/Format/Path.js",
          "../common/Drawings/Format/Image.js",
          "../common/Drawings/Format/GroupShape.js",
          "../common/Drawings/Format/ChartSpace.js",
          "../common/Drawings/Format/ChartFormat.js",
          "../common/Drawings/Format/TextBody.js",
          "../common/Drawings/Format/GraphicFrame.js",
          "../common/Charts/charts.js",
          "../common/Charts/DrawingArea.js",
          "../common/Charts/DrawingObjects.js",
          "../common/Charts/3DTransformation.js",
          "../common/Charts/ChartsDrawer.js",
          "../common/Drawings/TrackObjects/AdjustmentTracks.js",
          "../common/Drawings/TrackObjects/MoveTracks.js",
          "../common/Drawings/TrackObjects/NewShapeTracks.js",
          "../common/Drawings/TrackObjects/PolyLine.js",
          "../common/Drawings/TrackObjects/ResizeTracks.js",
          "../common/Drawings/TrackObjects/RotateTracks.js",
          "../common/Drawings/TrackObjects/Spline.js",
          "../common/Drawings/DrawingObjectsHandlers.js",
          "../common/Drawings/TextDrawer.js",

          "../common/Drawings/Externals.js",
          "../common/GlobalLoaders.js",
          "../common/CollaborativeEditingBase.js",
          "../common/Controls.js",
          "../common/Overlay.js",
          "../common/Drawings/HatchPattern.js",

          "../common/scroll.js",
          "../common/Scrolls/iscroll.js",
          "../common/Scrolls/mobileTouchManagerBase.js",

          "../common/wordcopypaste.js",

          "../cell/model/UndoRedo.js",
          "../cell/model/clipboard.js",
          "../cell/model/autofilters.js",
          "../cell/graphics/DrawingContext.js",
          "../cell/graphics/pdfprinter.js",
          "../cell/model/ConditionalFormatting.js",
          "../cell/model/FormulaObjects/parserFormula.js",
          "../cell/model/FormulaObjects/xlfnFunctions.js",
          "../cell/model/FormulaObjects/dateandtimeFunctions.js",
          "../cell/model/FormulaObjects/engineeringFunctions.js",
          "../cell/model/FormulaObjects/cubeFunctions.js",
          "../cell/model/FormulaObjects/databaseFunctions.js",
          "../cell/model/FormulaObjects/textanddataFunctions.js",
          "../cell/model/FormulaObjects/statisticalFunctions.js",
          "../cell/model/FormulaObjects/financialFunctions.js",
          "../cell/model/FormulaObjects/mathematicFunctions.js",
          "../cell/model/FormulaObjects/lookupandreferenceFunctions.js",
          "../cell/model/FormulaObjects/informationFunctions.js",
          "../cell/model/FormulaObjects/logicalFunctions.js",
          "../cell/model/CellComment.js",
          "../cell/model/WorkbookElems.js",
          "../cell/model/Workbook.js",
          "../cell/model/Serialize.js",
          "../cell/model/CellInfo.js",
          "../cell/view/mobileTouch.js",
          "../cell/view/StringRender.js",
          "../cell/view/CellTextRender.js",
          "../cell/view/CellEditorView.js",
          "../cell/view/EventsController.js",
          "../cell/view/WorkbookView.js",
          "../cell/view/WorksheetView.js",
          "../cell/view/DrawingObjectsController.js",
          "../cell/model/DrawingObjects/Graphics.js",
          "../cell/model/DrawingObjects/ShapeDrawer.js",
          "../cell/model/DrawingObjects/DrawingDocument.js",
          "../cell/model/DrawingObjects/GlobalCounters.js",
          "../cell/model/DrawingObjects/Format/ShapePrototype.js",
          "../cell/model/DrawingObjects/Format/ImagePrototype.js",
          "../cell/model/DrawingObjects/Format/GroupPrototype.js",
          "../cell/model/DrawingObjects/Format/ChartSpacePrototype.js",

          "../word/Editor/Comments.js",
          "../word/Editor/CommentsChanges.js",
          "../word/Editor/Styles.js",
          "../word/Editor/StylesChanges.js",
          "../word/Editor/FlowObjects.js",
          "../word/Editor/ParagraphContent.js",
          "../word/Editor/ParagraphContentBase.js",
          "../word/Editor/Paragraph/ParaTextPr.js",
          "../word/Editor/Paragraph/ParaTextPrChanges.js",
          "../word/Editor/Paragraph/ParaDrawing.js",
          "../word/Editor/Paragraph/ParaDrawingChanges.js",
          "../word/Editor/Hyperlink.js",
          "../word/Editor/HyperlinkChanges.js",
          "../word/Editor/Field.js",
          "../word/Editor/FieldChanges.js",
          "../word/Editor/Run.js",
          "../word/Editor/RunChanges.js",
          "../word/Editor/Math.js",
          "../word/Editor/MathChanges.js",
          "../word/Editor/Paragraph.js",
          "../word/Editor/ParagraphChanges.js",
          "../word/Editor/Paragraph_Recalculate.js",
          "../word/Editor/Sections.js",
          "../word/Editor/SectionsChanges.js",
          "../word/Editor/Numbering.js",
          "../word/Editor/NumberingChanges.js",
          "../word/Editor/HeaderFooter.js",
          "../word/Editor/DocumentContentBase.js",
          "../word/Editor/Document.js",
          "../word/Editor/DocumentChanges.js",
          "../word/Editor/DocumentContent.js",
          "../word/Editor/DocumentContentChanges.js",
          "../word/Editor/DocumentControllerBase.js",
          "../word/Editor/LogicDocumentController.js",
          "../word/Editor/DrawingsController.js",
          "../word/Editor/HeaderFooterController.js",
          "../word/Editor/Table.js",
          "../word/Editor/Table/TableChanges.js",
          "../word/Editor/Table/TableRecalculate.js",
          "../word/Editor/Table/TableDraw.js",
          "../word/Editor/Table/TableRow.js",
          "../word/Editor/Table/TableRowChanges.js",
          "../word/Editor/Table/TableCell.js",
          "../word/Editor/Table/TableCellChanges.js",
          "../word/Editor/Serialize2.js",
          "../word/Editor/Spelling.js",
          "../word/Editor/Footnotes.js",
          "../word/Editor/FootnotesChanges.js",
          "../word/Editor/FootEndNote.js",
          "../word/Editor/GraphicObjects/WrapManager.js",
          "../word/Editor/Common.js",
          "../word/Math/mathTypes.js",
          "../word/Math/mathText.js",
          "../word/Math/mathContent.js",
          "../word/Math/base.js",
          "../word/Math/fraction.js",
          "../word/Math/degree.js",
          "../word/Math/matrix.js",
          "../word/Math/limit.js",
          "../word/Math/nary.js",
          "../word/Math/radical.js",
          "../word/Math/operators.js",
          "../word/Math/accent.js",
          "../word/Math/borderBox.js",

          "../word/apiBuilder.js",
          "../slide/apiBuilder.js",
          "../cell/apiBuilder.js",

          "../common/clipboard_base.js",
          "../common/text_input.js",
          "../common/Drawings/Format/OleObject.js",
          "../common/Drawings/Format/DrawingContent.js",
          "../common/plugins.js",
          "../common/Local/common_jio.js",
          "../cell/Local/api_jio.js"
        ];
        break;
      case 'slide':
        list_files = [
          "../common/downloaderfiles.js",
          "../common/NumFormat.js",
          "../common/SerializeChart.js",

          "../common/FontsFreeType/font_engine.js",
          "../common/FontsFreeType/FontFile.js",
          "../common/FontsFreeType/font_map.js",
          "../common/FontsFreeType/FontManager.js",
          "../word/Editor/FontClassification.js",

          "../common/Drawings/Metafile.js",
          "../common/FontsFreeType/TextMeasurer.js",
          "../common/Drawings/WorkEvents.js",

          "../word/Editor/History.js",

          "../common/Shapes/EditorSettings.js",
          "../common/Shapes/Serialize.js",
          "../common/Shapes/SerializeWriter.js",

          "../common/Drawings/Hit.js",
          "../common/Drawings/ArcTo.js",
          "../common/Drawings/ColorArray.js",

          "../common/Drawings/CommonController.js",
          "../common/Drawings/States.js",
          "../common/Drawings/Format/CreateGeometry.js",
          "../common/Drawings/DrawingsChanges.js",
          "../common/Drawings/Format/Geometry.js",
          "../common/Drawings/Format/Format.js",
          "../common/Drawings/Format/GraphicObjectBase.js",
          "../common/Drawings/Format/Shape.js",
          "../slide/Editor/Format/ShapePrototype.js",
          "../common/Drawings/Format/Path.js",
          "../common/Drawings/Format/Image.js",
          "../common/Drawings/Format/GroupShape.js",
          "../common/Drawings/Format/ChartSpace.js",
          "../common/Drawings/Format/ChartFormat.js",
          "../common/Drawings/Format/TextBody.js",
          "../slide/Editor/Format/TextBodyPrototype.js",
          "../common/Drawings/Format/GraphicFrame.js",
          "../common/Charts/charts.js",
          "../common/Charts/DrawingArea.js",
          "../common/Charts/DrawingObjects.js",
          "../common/Charts/3DTransformation.js",
          "../common/Charts/ChartsDrawer.js",
          "../common/Drawings/TrackObjects/AdjustmentTracks.js",
          "../common/Drawings/TrackObjects/MoveTracks.js",
          "../common/Drawings/TrackObjects/NewShapeTracks.js",
          "../common/Drawings/TrackObjects/PolyLine.js",
          "../common/Drawings/TrackObjects/ResizeTracks.js",
          "../common/Drawings/TrackObjects/RotateTracks.js",
          "../common/Drawings/TrackObjects/Spline.js",
          "../common/Drawings/DrawingObjectsHandlers.js",
          "../common/Drawings/TextDrawer.js",

          "../common/Drawings/Externals.js",
          "../common/GlobalLoaders.js",
          "../common/Controls.js",
          "../common/Overlay.js",
          "../common/Drawings/HatchPattern.js",

          "../common/scroll.js",
          "../common/Scrolls/iscroll.js",
          "../common/Scrolls/mobileTouchManagerBase.js",
          "../slide/Drawing/mobileTouchManager.js",

          "../common/wordcopypaste.js",

          "../slide/themes/Themes.js",

          "../cell/utils/utils.js",
          "../cell/model/WorkbookElems.js",
          "../cell/model/Workbook.js",
          "../cell/model/Serialize.js",
          "../cell/model/CellInfo.js",
          "../cell/view/DrawingObjectsController.js",

          "../slide/Drawing/ThemeLoader.js",
          "../word/Editor/Serialize2.js",
          "../word/Editor/Styles.js",
          "../slide/Editor/Format/StylesPrototype.js",
          "../word/Editor/Numbering.js",
          "../word/Drawing/GraphicsEvents.js",
          "../word/Drawing/Rulers.js",
          "../word/Editor/Table.js",
          "../word/Editor/Table/TableChanges.js",
          "../word/Editor/Table/TableRecalculate.js",
          "../word/Editor/Table/TableDraw.js",
          "../word/Editor/Table/TableRow.js",
          "../word/Editor/Table/TableRowChanges.js",
          "../word/Editor/Table/TableCell.js",
          "../word/Editor/Table/TableCellChanges.js",
          "../word/Editor/Common.js",
          "../word/Editor/Sections.js",
          "../word/Editor/SectionsChanges.js",

          "../word/Drawing/Graphics.js",
          "../word/Drawing/ShapeDrawer.js",

          "../slide/Drawing/Transitions.js",
          "../slide/Drawing/DrawingDocument.js",
          "../slide/Drawing/HtmlPage.js",
          "../slide/Editor/Format/Presentation.js",
          "../slide/Editor/DrawingObjectsController.js",
          "../slide/Editor/Format/Slide.js",
          "../slide/Editor/Format/SlideMaster.js",
          "../slide/Editor/Format/Layout.js",
          "../slide/Editor/Format/Comments.js",
          "../word/Editor/Styles.js",
          "../word/Editor/StylesChanges.js",
          "../word/Editor/Numbering.js",
          "../word/Editor/NumberingChanges.js",
          "../word/Editor/ParagraphContent.js",
          "../word/Editor/ParagraphContentBase.js",
          "../word/Editor/Paragraph/ParaTextPr.js",
          "../word/Editor/Paragraph/ParaTextPrChanges.js",
          "../word/Editor/Paragraph/ParaDrawing.js",
          "../word/Editor/Paragraph/ParaDrawingChanges.js",
          "../word/Editor/Hyperlink.js",
          "../word/Editor/HyperlinkChanges.js",
          "../word/Editor/Field.js",
          "../word/Editor/FieldChanges.js",
          "../word/Editor/Run.js",
          "../word/Editor/RunChanges.js",
          "../word/Math/mathTypes.js",
          "../word/Math/mathText.js",
          "../word/Math/mathContent.js",
          "../word/Math/base.js",
          "../word/Math/fraction.js",
          "../word/Math/degree.js",
          "../word/Math/matrix.js",
          "../word/Math/limit.js",
          "../word/Math/nary.js",
          "../word/Math/radical.js",
          "../word/Math/operators.js",
          "../word/Math/accent.js",
          "../word/Math/borderBox.js",
          "../word/Editor/FlowObjects.js",
          "../word/Editor/Paragraph.js",
          "../word/Editor/ParagraphChanges.js",
          "../word/Editor/Paragraph_Recalculate.js",
          "../word/Editor/DocumentContentBase.js",
          "../word/Editor/Document.js",
          "../word/Editor/DocumentChanges.js",
          "../word/Editor/DocumentContent.js",
          "../word/Editor/DocumentContentChanges.js",
          "../word/Editor/DocumentControllerBase.js",
          "../word/Editor/LogicDocumentController.js",
          "../word/Editor/DrawingsController.js",
          "../word/Editor/HeaderFooterController.js",
          "../word/Editor/HeaderFooter.js",
          "../word/Editor/Math.js",
          "../word/Editor/MathChanges.js",
          "../word/Editor/Spelling.js",
          "../word/Editor/Footnotes.js",
          "../word/Editor/FootnotesChanges.js",
          "../word/Editor/FootEndNote.js",
          "../word/Editor/Search.js",

          "../slide/Editor/Format/ImagePrototype.js",
          "../slide/Editor/Format/GroupPrototype.js",
          "../slide/Editor/Format/ChartSpacePrototype.js",
          "../slide/apiCommon.js",

          "../word/apiBuilder.js",
          "../slide/apiBuilder.js",
          "../common/clipboard_base.js",
          "../common/text_input.js",
          "../common/Drawings/Format/OleObject.js",
          "../common/Drawings/Format/DrawingContent.js",
          "../common/plugins.js",
          "../common/Local/common_jio.js",
          "../slide/Local/api_jio.js"
        ];
        break;
    }

    list_files.forEach(function (url) {
      url = url.replace('../', './sdkjs/');
      queue.push(function () {
        return loadScript(url);
      });
    });
    queue.push(callback);
  }
};