<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="DTMLMethod" module="OFS.DTMLMethod"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.sheet.js</string> </value>
        </item>
        <item>
            <key> <string>_vars</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>globals</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>raw</string> </key>
            <value> <string>/*\n
jQuery.sheet() The Web Based Spreadsheet\n
$Id: jquery.sheet.js 301 2010-11-09 12:59:13Z RobertLeePlummerJr $\n
http://code.google.com/p/jquerysheet/\n
    \n
Copyright (C) 2010 Robert Plummer\n
Dual licensed under the LGPL v2 and GPL v2 licenses.\n
http://www.gnu.org/licenses/\n
*/\n
\n
/*\n
  Dimensions Info:\n
    When dealing with size, it seems that outerHeight is generally the most stable cross browser\n
    attribute to use for bar sizing.  We try to use this as much as possible.  But because col\'s\n
    don\'t have boarders, we subtract or add jS.s.boxModelCorrection for those browsers.\n
  tr/td column and row Index VS cell/column/row index\n
    DOM elements are all 0 based (tr/td/table)\n
    Spreadsheet elements are all 1 based (A1, A1:B4, TABLE2:A1, TABLE2:A1:B4)\n
    Column/Row/Cell\n
  DOCTYPE:\n
    It is recommended to use STRICT doc types on the viewing page when using sheet to ensure that the heights/widths of bars and sheet rows show up correctly\n
    Example of recommended doc type: \074!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"\076\n
*/\n
jQuery.fn.extend({\n
  sheet: function(settings) {\n
    var o;\n
    settings = jQuery.extend({\n
      urlGet:       "sheets/enduser.documentation.html", //local url, if you want to get a sheet from a url\n
      urlSave:      "save.html",          //local url, for use only with the default save for sheet\n
      editable:       true,               //bool, Makes the jSheetControls_formula \046 jSheetControls_fx appear\n
      allowToggleState:   true,             //allows the function that changes the spreadsheet\'s state from static to editable and back\n
      urlMenu:      "menu.html",          //local url, for the menu to the right of title\n
      newColumnWidth:   120,              //int, the width of new columns or columns that have no width assigned\n
      title:        null,               //html, general title of the sheet group\n
      inlineMenu:     null,               //html, menu for editing sheet\n
      buildSheet:     false,              //bool, string, or object\n
                                  //bool true - build sheet inside of parent\n
                                  //bool false - use urlGet from local url\n
                                  //string  - \'{number_of_cols}x{number_of_rows} (5x100)\n
                                  //object - table\n
      calcOff:      false,              //bool, turns calculationEngine off (no spreadsheet, just grid)\n
      log:        false,              //bool, turns some debugging logs on (jS.log(\'msg\'))\n
      lockFormulas:     false,              //bool, turns the ability to edit any formula off\n
      parent:       jQuery(this),           //object, sheet\'s parent, DON\'T CHANGE\n
      colMargin:      18,               //int, the height and the width of all bar items, and new rows\n
      fnBefore:       function() {},          //fn, called just before jQuery.sheet loads\n
      fnAfter:      function() {},          //fn, called just after all sheets load\n
      fnSave:       function() { o.sheetInstance.saveSheet(); }, //fn, default save function, more of a proof of concept\n
      fnOpen:       function() {          //fn, by default allows you to paste table html into a javascript prompt for you to see what it looks likes if you where to use sheet\n
                  var t = prompt(\'Paste your table html here\');\n
                  if (t) {\n
                    o.sheetInstance.openSheet(t);\n
                  }\n
      },\n
      fnClose:      function() {},          //fn, default clase function, more of a proof of concept\n
      fnAfterCellEdit:  function() {},          //fn, called just after someone edits a cell\n
      fnSwitchSheet:    function() {},          //fn, called when a spreadsheet is switched inside of an instance of sheet\n
      fnPaneScroll:   function() {},          //fn, called when a spreadsheet is scrolled\n
      joinedResizing:   false,              //bool, this joins the column/row with the resize bar\n
      boxModelCorrection: 2,                //int, attempts to correct the differences found in heights and widths of different browsers, if you mess with this, get ready for the must upsetting and delacate js ever\n
      showErrors:     true,             //bool, will make cells value an error if spreadsheet function isn\'t working correctly or is broken\n
      calculations:   {},               //object, used to extend the standard functions that come with sheet\n
      cellSelectModel:  \'excel\',            //string, \'excel\' || \'oo\' || \'gdocs\' Excel sets the first cell onmousedown active, openoffice sets the last, now you can choose how you want it to be ;)\n
      autoAddCells:   true,             //bool, when user presses enter on the last row, this will allow them to add another cell, thus improving performance and optimizing modification speed\n
      caseInsensitive:  false,              //bool, this makes all the calculations engine user functions case sensitive/insensitive\n
      resizable:      true,             //bool, makes the $(obj).sheet(); object resizeable, also adds a resizable formula textarea at top of sheet\n
      autoFiller:     false,              //bool, the little guy that hangs out to the bottom right of a selected cell, users can click and drag the value to other cells\n
      minSize:      {rows: 1, cols: 1},      //object - {rows: int, cols: int}, Makes the sheet stay at a certain size when loaded in edit mode, to make modification more productive\n
      forceColWidthsOnStartup:true            //bool, makes cell widths load from pre-made colgroup/col objects, use this if you plan on making the col items, makes widths more stable on startup\n
    }, settings);\n
    \n
    o = settings.parent;\n
    if (jQuery.sheet.instance) {\n
      o.sheetInstance = jQuery.sheet.createInstance(settings, jQuery.sheet.instance.length, o);\n
      jQuery.sheet.instance.push(o.sheetInstance);\n
    } else {\n
      o.sheetInstance = jQuery.sheet.createInstance(settings, 0, o);\n
      jQuery.sheet.instance = [o.sheetInstance];\n
    }\n
    return o;\n
  }\n
});\n
\n
jQuery.sheet = {\n
  createInstance: function(s, I, origParent) { //s = jQuery.sheet settings, I = jQuery.sheet Instance Integer\n
    var jS = {\n
      version: \'1.2.0\',\n
      i: 0,\n
      I: I,\n
      sheetCount: 0,\n
      s: {},//s = settings object, used for shorthand, populated from jQuery.sheet\n
      obj: {//obj = object references\n
        //Please note, class references use the tag name because it\'s about 4 times faster\n
        autoFiller:     function() { return jQuery(\'#\' + jS.id.autoFiller + jS.i); },\n
        barCorner:      function() { return jQuery(\'#\' + jS.id.barCorner + jS.i); },\n
        barCornerAll:   function() { return s.parent.find(\'div.\' + jS.cl.barCorner); },\n
        barCornerParent:  function() { return jQuery(\'#\' + jS.id.barCornerParent + jS.i); },\n
        barCornerParentAll: function() { return s.parent.find(\'td.\' + jS.cl.barCornerParent); },\n
        barTop:       function() { return jQuery(\'#\' + jS.id.barTop + jS.i); },\n
        barTopAll:      function() { return s.parent.find(\'div.\' + jS.cl.barTop); },\n
        barTopParent:     function() { return jQuery(\'#\' + jS.id.barTopParent + jS.i); },\n
        barTopParentAll:  function() { return s.parent.find(\'div.\' + jS.cl.barTopParent); },\n
        barLeft:      function() { return jQuery(\'#\' + jS.id.barLeft + jS.i); },\n
        barLeftAll:     function() { return s.parent.find(\'div.\' + jS.cl.barLeft); },\n
        barLeftParent:    function() { return jQuery(\'#\' + jS.id.barLeftParent + jS.i); },\n
        barLeftParentAll: function() { return s.parent.find(\'div.\' + jS.cl.barLeftParent); },\n
        cellActive:     function() { return jQuery(jS.cellLast.td); },\n
        cellHighlighted:  function() { return jQuery(jS.highlightedLast.td); },\n
        chart:        function() { return jQuery(\'div.\' + jS.cl.chart); },\n
        controls:     function() { return jQuery(\'#\' + jS.id.controls); },\n
        formula:      function() { return jQuery(\'#\' + jS.id.formula); },\n
        fullScreen:     function() { return jQuery(\'div.\' + jS.cl.fullScreen); },\n
        inlineMenu:     function() { return jQuery(\'#\' + jS.id.inlineMenu); },\n
        inPlaceEdit:    function() { return jQuery(\'#\' + jS.id.inPlaceEdit); },\n
        label:        function() { return jQuery(\'#\' + jS.id.label); },\n
        log:        function() { return jQuery(\'#\' + jS.id.log); },\n
        menu:       function() { return jQuery(\'#\' + jS.id.menu); },\n
        pane:         function() { return jQuery(\'#\' + jS.id.pane + jS.i); },\n
        paneAll:      function() { return s.parent.find(\'div.\' + jS.cl.pane); },\n
        parent:       function() { return s.parent; },\n
        sheet:        function() { return jQuery(\'#\' + jS.id.sheet + jS.i); },\n
        sheetAll:       function() { return s.parent.find(\'table.\' + jS.cl.sheet); },\n
        tab:        function() { return jQuery(\'#\' + jS.id.tab + jS.i); },\n
        tabAll:       function() { return this.tabContainer().find(\'a.\' + jS.cl.tab); },\n
        tabContainer:   function() { return jQuery(\'#\' + jS.id.tabContainer); },\n
        tableBody:      function() { return document.getElementById(jS.id.sheet + jS.i); },\n
        tableControl:   function() { return jQuery(\'#\' + jS.id.tableControl + jS.i); },\n
        tableControlAll:  function() { return s.parent.find(\'table.\' + jS.cl.tableControl); },\n
        title:        function() { return jQuery(\'#\' + jS.id.title); },\n
        ui:         function() { return jQuery(\'#\' + jS.id.ui); },\n
        uiActive:     function() { return s.parent.find(\'div.\' + jS.cl.uiActive); }\n
      },\n
      id: {\n
        /*\n
          id = id\'s references\n
          Note that these are all dynamically set\n
        */\n
        autoFiller:     \'jSheetAutoFiller_\' + I + \'_\',\n
        barCorner:      \'jSheetBarCorner_\' + I + \'_\',\n
        barCornerParent:  \'jSheetBarCornerParent_\' + I + \'_\',\n
        barTop:       \'jSheetBarTop_\' + I + \'_\',\n
        barTopParent:     \'jSheetBarTopParent_\' + I + \'_\',\n
        barLeft:      \'jSheetBarLeft_\' + I + \'_\',\n
        barLeftParent:    \'jSheetBarLeftParent_\' + I + \'_\',\n
        controls:     \'jSheetControls_\' + I,\n
        formula:      \'jSheetControls_formula_\' + I,\n
        inlineMenu:     \'jSheetInlineMenu_\' + I,\n
        inPlaceEdit:    \'jSheetInPlaceEdit_\' + I,\n
        label:        \'jSheetControls_loc_\' + I,\n
        log:        \'jSheetLog_\' + I,\n
        menu:       \'jSheetMenu_\' + I,\n
        pane:         \'jSheetEditPane_\' + I + \'_\',\n
        sheet:        \'jSheet_\' + I + \'_\',\n
        tableControl:   \'tableControl_\' + I + \'_\',\n
        tab:        \'jSheetTab_\' + I + \'_\',\n
        tabContainer:   \'jSheetTabContainer_\' + I,\n
        title:        \'jSheetTitle_\' + I,\n
        ui:         \'jSheetUI_\' + I\n
      },\n
      cl: {\n
        /*\n
          cl = class references\n
        */\n
        autoFiller:       \'jSheetAutoFiller\',\n
        autoFillerHandle:   \'jSheetAutoFillerHandle\',\n
        autoFillerConver:   \'jSheetAutoFillerCover\',\n
        barCorner:        \'jSheetBarCorner\',\n
        barCornerParent:    \'jSheetBarCornerParent\',\n
        barLeftTd:        \'barLeft\',\n
        barLeft:        \'jSheetBarLeft\',\n
        barLeftParent:      \'jSheetBarLeftParent\',\n
        barTop:         \'jSheetBarTop\',\n
        barTopParent:       \'jSheetBarTopParent\',\n
        barTopTd:       \'barTop\',\n
        cellActive:       \'jSheetCellActive\',\n
        cellHighlighted:    \'jSheetCellHighighted\',\n
        chart:          \'jSheetChart\',\n
        controls:       \'jSheetControls\',\n
        formula:        \'jSheetControls_formula\',\n
        inlineMenu:       \'jSheetInlineMenu\',\n
        fullScreen:       \'jSheetFullScreen\',\n
        inPlaceEdit:      \'jSheetInPlaceEdit\',\n
        menu:         \'jSheetMenu\',\n
        parent:         \'jSheetParent\',\n
        sheet:          \'jSheet\',\n
        sheetPaneTd:      \'sheetPane\',\n
        label:          \'jSheetControls_loc\',\n
        log:          \'jSheetLog\',\n
        pane:           \'jSheetEditPane\',\n
        tab:          \'jSheetTab\',\n
        tabContainer:     \'jSheetTabContainer\',\n
        tabContainerFullScreen: \'jSheetFullScreenTabContainer\',\n
        tableControl:     \'tableControl\',\n
        title:          \'jSheetTitle\',\n
        toggle:         \'cellStyleToggle\',\n
        ui:           \'jSheetUI\',\n
        uiAutoFiller:     \'ui-state-active\',\n
        uiActive:       \'ui-state-active\',\n
        uiBar:          \'ui-widget-header\',\n
        uiCellActive:     \'ui-state-active\',\n
        uiCellHighlighted:    \'ui-state-highlight\',\n
        uiControl:        \'ui-widget-header ui-corner-top\',\n
        uiControlTextBox:   \'ui-widget-content\',\n
        uiFullScreen:     \'ui-widget-content ui-corner-all\',\n
        uiInPlaceEdit:      \'ui-state-active\',\n
        uiMenu:         \'ui-state-highlight\',\n
        uiMenuUl:         \'ui-widget-header\',\n
        uiMenuLi:         \'ui-widget-header\',\n
        uiMenuHighlighted:    \'ui-state-highlight\',\n
        uiPane:         \'ui-widget-content\',\n
        uiParent:         \'ui-widget-content ui-corner-all\',\n
        uiSheet:        \'ui-widget-content\',\n
        uiTab:          \'ui-widget-header\',\n
        uiTabActive:      \'ui-state-highlight\'\n
      },\n
      msg: { /*msg = messages used throught sheet, for easy access to change them for other languages*/\n
        addRowMulti:    "How many rows would you like to add?",\n
        addColumnMulti:   "How many columns would you like to add?",\n
        newSheet:       "What size would you like to make your spreadsheet? Example: \'5x10\' creates a sheet that is 5 columns by 10 rows.",\n
        deleteRow:      "Are you sure that you want to delete that row?",\n
        deleteColumn:     "Are you sure that you want to delete that column?",\n
        openSheet:      "Are you sure you want to open a different sheet?  All unsaved changes will be lost.",\n
        cellFind:       "No results found.",\n
        toggleHideRow:    "No row selected.",\n
        toggleHideColumn:   "Now column selected.",\n
        merge:        "Merging is not allowed on the first row.",\n
        evalError:      "Error, functions as formulas not supported."\n
      },\n
      kill: function() { /* For ajax manipulation, kills this instance of sheet entirley */\n
        jS.obj.tabContainer().remove();\n
        jS.obj.fullScreen().remove();\n
        jS.obj.inPlaceEdit().remove();\n
        origParent.removeClass(jS.cl.uiParent).html(\'\');\n
        cE = s = jQuery.sheet.instance[I] = jS = origParent.sheetInstance = null;\n
        delete cE;\n
        delete s;\n
        delete jQuery.sheet.instance[I];\n
        delete jS;\n
        delete origParent.sheetInstance;\n
      },\n
      controlFactory: { /* controlFactory creates the different objects requied by sheet */\n
        addRowMulti: function(qty, isBefore, skipFormulaReparse) { /* creates multi rows\n
                              qty: int, the number of cells you\'d like to add, if not specified, a dialog will ask; \n
                              isBefore: bool, places cells before the selected cell if set to true, otherwise they will go after, or at end\n
                              skipFormulaReparse: bool, re-parses formulas if needed\n
                            */\n
          if (!qty) {\n
            qty = prompt(jS.msg.addRowMulti);\n
          }\n
          if (qty) {\n
            jS.controlFactory.addCells(null, isBefore, null, qty, \'row\', skipFormulaReparse);\n
          }\n
        },\n
        addColumnMulti: function(qty, isBefore, skipFormulaReparse) { /* creates multi columns\n
                              qty: int, the number of cells you\'d like to add, if not specified, a dialog will ask; \n
                              isBefore: bool, places cells before the selected cell if set to true, otherwise they will go after, or at end\n
                              skipFormulaReparse: bool, re-parses formulas if needed\n
                            */\n
          if (!qty) {\n
            qty = prompt(jS.msg.addColumnMulti);\n
          }\n
          if (qty) {\n
            jS.controlFactory.addCells(null, isBefore, null, qty, \'col\', skipFormulaReparse);\n
          }\n
        },\n
        addCells: function(eq, isBefore, eqO, qty, type, skipFormulaReparse) { /*creates cells for sheet and the bars that go along with them\n
                                    eq: int, position where cells should be added;\n
                                    isBefore: bool, places cells before the selected cell if set to true, otherwise they will go after, or at end;\n
                                    eq0: no longer used, kept for legacy;\n
                                    qty: int, how many rows/columsn to add;\n
                                    type: string - "col" || "row", determans the type of cells to add;\n
                                    skipFormulaReparse: bool, re-parses formulas if needed\n
                                */\n
          //hide the autoFiller, it can get confused\n
          if (s.autoFiller) {\n
            jS.obj.autoFiller().hide();\n
          }\n
          \n
          jS.setDirty(true);\n
          \n
          var sheet = jS.obj.sheet();\n
          var sheetWidth = sheet.width();\n
          \n
          //jS.evt.cellEditAbandon();\n
          \n
          qty = (qty ? qty : 1);\n
          type = (type ? type : \'col\');\n
          \n
          //var barLast = (type == \'row\' ? jS.rowLast : jS.colLast);\n
          var cellLastBar = (type == \'row\' ? jS.cellLast.row : jS.cellLast.col);\n
          \n
          if (!eq) {\n
            if (cellLastBar == -1) {\n
              eq = \':last\';\n
            } else {\n
              eq = \':eq(\' + cellLastBar + \')\';\n
            }\n
          } else if (!isNaN(eq)){\n
            eq = \':eq(\' + (eq - 1) + \')\';\n
          }\n
          \n
          var o;\n
          switch (type) {\n
            case "row":\n
              o = {\n
                bar: jS.obj.barLeft().find(\'div\' + eq),\n
                barParent: jS.obj.barLeft(),\n
                cells: function() {\n
                  return sheet.find(\'tr\' + eq);\n
                },\n
                col: function() { return \'\'; },\n
                newBar: \'\074div class="\' + jS.cl.uiBar + \'" style="height: \' + (s.colMargin - s.boxModelCorrection) + \'px;" /\076\',\n
                loc: function() {\n
                  return jS.getTdLocation(o.cells().find(\'td:last\'));\n
                },\n
                newCells: function() {\n
                  var j = o.loc()[1];\n
                  var newCells = \'\';\n
                  \n
                  for (var i = 0; i \074= j; i++) {\n
                    newCells += \'\074td /\076\';\n
                  }\n
                  \n
                  return \'\074tr style="height: \' + s.colMargin + \'px;"\076\' + newCells + \'\074/tr\076\';\n
                },\n
                newCol: \'\',\n
                reLabel: function() {               \n
                  o.barParent.children().each(function(i) {\n
                    jQuery(this).text(i + 1);\n
                  });\n
                },\n
                dimensions: function(loc, bar, cell, col) {\n
                  bar.height(cell.height(s.colMargin).outerHeight() - s.boxModelCorrection);\n
                },\n
                offset: [qty, 0]\n
              };\n
              break;\n
            case "col":\n
              o = {\n
                bar: jS.obj.barTop().find(\'div\' + eq),\n
                barParent: jS.obj.barTop(),\n
                cells: function() {\n
                  var cellStart = sheet.find(\'tr:first td\' + eq);\n
                  if (!cellStart[0]) {\n
                    cellStart = sheet.find(\'tr:first th\' + eq);\n
                  }\n
                  var cellEnd = sheet.find(\'td:last\');\n
                  var loc1 = jS.getTdLocation(cellStart);\n
                  var loc2 = jS.getTdLocation(cellEnd);\n
                  \n
                  //we get the first cell then get all the other cells directly... faster ;)\n
                  var cells = jQuery(jS.getTd(jS.i, loc1[0], loc1[1]));\n
                  var cell;\n
                  for (var i = 1; i \074= loc2[0]; i++) {\n
                    cells.push(jS.getTd(jS.i, i, loc1[1]));\n
                  }\n
                  \n
                  return cells;\n
                },\n
                col: function() {\n
                  return sheet.find(\'col\' + eq);\n
                },\n
                newBar: \'\074div class="\' + jS.cl.uiBar + \'"/\076\',\n
                newCol: \'\074col /\076\',\n
                loc: function(cells) {\n
                  cells = (cells ? cells : o.cells());\n
                  return jS.getTdLocation(cells.first());\n
                },\n
                newCells: function() {\n
                  return \'\074td /\076\';\n
                },\n
                reLabel: function() {\n
                  o.barParent.children().each(function(i) {\n
                    jQuery(this).text(cE.columnLabelString(i + 1));\n
                  });\n
                },\n
                dimensions: function(loc, bar, cell, col) {               \n
                  var w = s.newColumnWidth;\n
                  col\n
                    .width(w)\n
                    .css(\'width\', w + \'px\')\n
                    .attr(\'width\', w + \'px\');\n
                  \n
                  bar\n
                    .width(w - s.boxModelCorrection);\n
                  \n
                  sheet.width(sheetWidth + (w * qty));\n
                },\n
                offset: [0, qty]\n
              };\n
              break;\n
          }\n
          \n
          //make undoable\n
          jS.cellUndoable.add(jQuery(sheet).add(o.barParent));\n
          \n
          var cells = o.cells();\n
          var loc = o.loc(cells); \n
          var col = o.col();\n
          \n
          var newBar = o.newBar;\n
          var newCell = o.newCells();\n
          var newCol = o.newCol;\n
          \n
          var newCols = \'\';\n
          var newBars = \'\';\n
          var newCells = \'\';\n
          \n
          for (var i = 0; i \074 qty; i++) { //by keeping these variables strings temporarily, we cut down on using system resources\n
            newCols += newCol;\n
            newBars += newBar;\n
            newCells += newCell;\n
          }\n
          \n
          newCols = jQuery(newCols);\n
          newBars = jQuery(newBars);\n
          newCells = jQuery(newCells);\n
          \n
          if (isBefore) {\n
            cells.before(newCells);\n
            o.bar.before(newBars);\n
            jQuery(col).before(newCols);\n
          } else {\n
            cells.after(newCells);\n
            o.bar.after(newBars);\n
            jQuery(col).after(newCols);\n
          }\n
          \n
          jS.setTdIds(sheet);\n
          \n
          o.dimensions(loc, newBars, newCells, newCols);\n
          o.reLabel();\n
\n
          jS.obj.pane().scroll();\n
          \n
          if (!skipFormulaReparse \046\046 eq != \':last\' \046\046 !isBefore) {\n
            //offset formulas\n
            jS.offsetFormulaRange((isBefore ? loc[0] - qty : loc[0]) , (isBefore ? loc[1] - qty : loc[0]), o.offset[0], o.offset[1], isBefore);\n
          }\n
          \n
          //Because the line numbers get bigger, it is possible that the bars have changed in size, lets sync them\n
          jS.sheetSyncSize();\n
          \n
          //Let\'s make it redoable\n
          jS.cellUndoable.add(jQuery(sheet).add(o.barParent));\n
        },\n
        addRow: function(atRow, isBefore, atRowQ) {/* creates single row\n
                              qty: int, the number of cells you\'d like to add, if not specified, a dialog will ask; \n
                              isBefore: bool, places cells before the selected cell if set to true, otherwise they will go after, or at end\n
                            */\n
          jS.controlFactory.addCells(atRow, isBefore, atRowQ, 1, \'row\');\n
        },\n
        addColumn: function(atColumn, isBefore, atColumnQ) {/* creates single column\n
                              qty: int, the number of cells you\'d like to add, if not specified, a dialog will ask; \n
                              isBefore: bool, places cells before the selected cell if set to true, otherwise they will go after, or at end\n
                            */\n
          jS.controlFactory.addCells(atColumn, isBefore, atColumnQ, 1, \'col\');\n
        },\n
        barLeft: function(reloadHeights, o) { /* creates all the bars to the left of the spreadsheet\n
                              reloadHeights: bool, reloads all the heights of each bar from the cells of the sheet;\n
                              o: object, the table/spreadsheeet object\n
                          */\n
          jS.obj.barLeft().remove();\n
          var barLeft = jQuery(\'\074div border="1px" id="\' + jS.id.barLeft + jS.i + \'" class="\' + jS.cl.barLeft + \'" /\076\');\n
          var heightFn;\n
          if (reloadHeights) { //This is our standard way of detecting height when a sheet loads from a url\n
            heightFn = function(i, objSource, objBar) {\n
              objBar.height(parseInt(objSource.outerHeight()) - s.boxModelCorrection);\n
            };\n
          } else { //This way of detecting height is used becuase the object has some problems getting\n
              //height because both tr and td have height set\n
              //This corrects the problem\n
              //This is only used when a sheet is already loaded in the pane\n
            heightFn = function(i, objSource, objBar) {\n
              objBar.height(parseInt(objSource.css(\'height\').replace(\'px\',\'\')) - s.boxModelCorrection);\n
            };\n
          }\n
          \n
          o.find(\'tr\').each(function(i) {\n
            var child = jQuery(\'\074div\076\' + (i + 1) + \'\074/div\076\');\n
            jQuery(barLeft).append(child);\n
            heightFn(i, jQuery(this), child);\n
          });\n
          \n
          jS.evt.barMouseDown.height(\n
            jS.obj.barLeftParent().append(barLeft)\n
          );\n
        },\n
        barTop: function(reloadWidths, o) { /* creates all the bars to the top of the spreadsheet\n
                              reloadWidths: bool, reloads all the widths of each bar from the cells of the sheet;\n
                              o: object, the table/spreadsheeet object\n
                          */\n
          jS.obj.barTop().remove();\n
          var barTop = jQuery(\'\074div id="\' + jS.id.barTop + jS.i + \'" class="\' + jS.cl.barTop + \'" /\076\');\n
          barTop.height(s.colMargin);\n
          \n
          var parents;\n
          var widthFn;\n
          \n
          if (reloadWidths) {\n
            parents = o.find(\'tr:first\').find(\'td,th\');\n
            widthFn = function(obj) {\n
              return jS.attrH.width(obj);\n
            };\n
          } else {\n
            parents = o.find(\'col\');\n
            widthFn = function(obj) {\n
              return parseInt(jQuery(obj).css(\'width\').replace(\'px\',\'\')) - s.boxModelCorrection;\n
            };\n
          }\n
          \n
          parents.each(function(i) {\n
            var v = cE.columnLabelString(i + 1);\n
            var w = widthFn(this);\n
            \n
            var child = jQuery("\074div\076" + v + "\074/div\076")\n
              .width(w)\n
              .height(s.colMargin);\n
            barTop.append(child);\n
          });\n
          \n
          jS.evt.barMouseDown.width(\n
            jS.obj.barTopParent().append(barTop)\n
          );\n
        },\n
        header: function() { /* creates the control/container for everything above the spreadsheet */\n
          jS.obj.controls().remove();\n
          jS.obj.tabContainer().remove();\n
          \n
          var header = jQuery(\'\074div id="\' + jS.id.controls + \'" class="\' + jS.cl.controls + \'"\076\074/div\076\');\n
          \n
          var firstRow = jQuery(\'\074table cellpadding="0" cellspacing="0" border="0"\076\074tr /\076\074/table\076\').prependTo(header);\n
          var firstRowTr = jQuery(\'\074tr /\076\');\n
          \n
          if (s.title) {\n
            var title;\n
            if (jQuery.isFunction(s.title)) {\n
              title = jS.title(jS);\n
            } else {\n
              title = s.title;\n
            }\n
            firstRowTr.append(jQuery(\'\074td id="\' + jS.id.title + \'" class="\' + jS.cl.title + \'" /\076\').html(title));\n
          }\n
          \n
          if (s.inlineMenu \046\046 s.editable) {\n
            var inlineMenu;\n
            if (jQuery.isFunction(s.inlineMenu)) {\n
              inlineMenu = s.inlineMenu(jS);\n
            } else {\n
              inlineMenu = s.inlineMenu;\n
            }\n
            firstRowTr.append(jQuery(\'\074td id="\' + jS.id.inlineMenu + \'" class="\' + jS.cl.inlineMenu + \'" /\076\').html(inlineMenu));\n
          }\n
          \n
          if (s.editable) {\n
            //Page Menu Control \n
            if (jQuery.mbMenu) {\n
              jQuery(\'\074div /\076\').load(s.urlMenu, function() {\n
                var menu = jQuery(\'\074td style="width: 50px; text-align: center;" id="\' + jS.id.menu + \'" class="rootVoices ui-corner-tl \' + jS.cl.menu + \'" /\076\')\n
                  .html(\n
                    jQuery(this).html()\n
                      .replace(/sheetInstance/g, "jQuery.sheet.instance[" + I + "]")\n
                      .replace(/menuInstance/g, I));\n
                      \n
                  menu\n
                    .prependTo(firstRowTr)\n
                    .buildMenu({\n
                      menuWidth:    100,\n
                      openOnRight:  false,\n
                      containment:  s.parent.attr(\'id\'),\n
                      hasImages:    false,\n
                      fadeInTime:   0,\n
                      fadeOutTime:  0,\n
                      adjustLeft:   2,\n
                      minZindex:    "auto",\n
                      adjustTop:    10,\n
                      opacity:    .95,\n
                      shadow:     false,\n
                      closeOnMouseOut:true,\n
                      closeAfter:   1000,\n
                      hoverIntent:  0, //if you use jquery.hoverIntent.js set this to time in milliseconds; 0= false;\n
                      submenuHoverIntent: 0\n
                    })\n
                    .hover(function() {\n
                      //not going to add to jS.cl because this isn\'t our control\n
                      jQuery(this).addClass(jS.cl.uiMenu);\n
                    }, function() {\n
                      jQuery(this).removeClass(jS.cl.uiMenu);\n
                    });\n
              });\n
            }\n
            \n
            //Edit box menu\n
            var secondRow = jQuery(\'\074table cellpadding="0" cellspacing="0" border="0"\076\' +\n
                \'\074tr\076\' +\n
                  \'\074td id="\' + jS.id.label + \'" class="\' + jS.cl.label + \'"\076\074/td\076\' +\n
                  \'\074td\076\' +\n
                    \'\074textarea id="\' + jS.id.formula + \'" class="\' + jS.cl.formula + \'"\076\074/textarea\076\' +\n
                  \'\074/td\076\' +\n
                \'\074/tr\076\' +\n
              \'\074/table\076\')\n
              .keydown(jS.evt.keyDownHandler.formulaOnKeyDown)\n
              .keyup(function() {\n
                jS.obj.inPlaceEdit().val(jS.obj.formula().val());\n
              })\n
              .change(function() {\n
                jS.obj.inPlaceEdit().val(jS.obj.formula().val());\n
              })\n
              .appendTo(header);\n
          }\n
          \n
          firstRowTr.appendTo(firstRow);\n
          \n
          var tabParent = jQuery(\'\074div id="\' + jS.id.tabContainer + \'" class="\' + jS.cl.tabContainer + \'"\076\' + \n
                  (s.editable ? \'\074span class="\' + jS.cl.uiTab + \' ui-corner-bottom" title="Add a spreadsheet" i="-1"\076+\074/span\076\' : \'\074span /\076\') + \n
                \'\074/div\076\')\n
              .mousedown(jS.evt.tabOnMouseDown);\n
\n
          s.parent\n
            .html(\'\')\n
            .append(header) //add controls header\n
            .append(\'\074div id="\' + jS.id.ui + \'" class="\' + jS.cl.ui + \'"\076\') //add spreadsheet control\n
            .after(tabParent);\n
        },\n
        sheetUI: function(o, i, fn, reloadBars) { /* creates the spreadsheet user interface\n
                              o: object, table object to be used as a spreadsheet;\n
                              i: int, the new count for spreadsheets in this instance;\n
                              fn: function, called after the spreadsheet is created and tuned for use;\n
                              reloadBars: bool, if set to true reloads id bars on top and left;\n
                            */\n
          if (!i) {\n
            jS.sheetCount = 0;\n
            jS.i = 0;\n
          } else {\n
            jS.sheetCount = parseInt(i);\n
            jS.i = jS.sheetCount;\n
            i = jS.i;\n
          }\n
\n
          var objContainer = jS.controlFactory.table().appendTo(jS.obj.ui());\n
          var pane = jS.obj.pane().html(o);\n
          \n
          if (s.autoFiller \046\046 s.editable) {\n
            pane.append(jS.controlFactory.autoFiller());\n
          }\n
          \n
          o = jS.tuneTableForSheetUse(o);\n
                \n
          jS.sheetDecorate(o);\n
          \n
          jS.controlFactory.barTop(reloadBars, o);\n
          jS.controlFactory.barLeft(reloadBars, o);\n
        \n
          jS.sheetTab(true);\n
          \n
          if (s.editable) {\n
            var formula = jS.obj.formula();\n
            pane\n
              .mousedown(function(e) {\n
                if (jS.isTd(e.target)) {\n
                  jS.evt.cellOnMouseDown(e);\n
                  return false;\n
                }\n
              })\n
              .disableSelection()\n
              .dblclick(jS.evt.cellOnDblClick);\n
          }\n
          \n
          jS.themeRoller.start(i);\n
\n
          jS.setTdIds(o);\n
          \n
          jS.checkMinSize(o);\n
          \n
          jS.evt.scrollBars(pane);\n
          \n
          jS.addTab();\n
          \n
          if (fn) {\n
            fn(objContainer, pane);\n
          }\n
          \n
          jS.log(\'Sheet Initialized\');\n
          \n
          return objContainer;\n
        },\n
        table: function() { /* creates the table control the will contain all the other controls for this instance */\n
          return jQuery(\'\074table cellpadding="0" cellspacing="0" border="0" id="\' + jS.id.tableControl + jS.i + \'" class="\' + jS.cl.tableControl + \'"\076\' +\n
            \'\074tbody\076\' +\n
              \'\074tr\076\' + \n
                \'\074td id="\' + jS.id.barCornerParent + jS.i + \'" class="\' + jS.cl.barCornerParent + \'"\076\' + //corner\n
                  \'\074div style="height: \' + s.colMargin + \'; width: \' + s.colMargin + \';" id="\' + jS.id.barCorner + jS.i + \'" class="\' + jS.cl.barCorner +\'"\' + (s.editable ? \' onClick="jQuery.sheet.instance[\' + I + \'].cellSetActiveBar(\\\'all\\\');"\' : \'\') + \' title="Select All"\076\046nbsp;\074/div\076\' +\n
                \'\074/td\076\' + \n
                \'\074td class="\' + jS.cl.barTopTd + \'"\076\' + //barTop\n
                  \'\074div id="\' + jS.id.barTopParent + jS.i + \'" class="\' + jS.cl.barTopParent + \'"\076\074/div\076\' +\n
                \'\074/td\076\' +\n
              \'\074/tr\076\' +\n
              \'\074tr\076\' +\n
                \'\074td class="\' + jS.cl.barLeftTd + \'"\076\' + //barLeft\n
                  \'\074div style="width: \' + s.colMargin + \';" id="\' + jS.id.barLeftParent + jS.i + \'" class="\' + jS.cl.barLeftParent + \'"\076\074/div\076\' +\n
                \'\074/td\076\' +\n
                \'\074td class="\' + jS.cl.sheetPaneTd + \'"\076\' + //pane\n
                  \'\074div id="\' + jS.id.pane + jS.i + \'" class="\' + jS.cl.pane + \'"\076\074/div\076\' +\n
                \'\074/td\076\' +\n
              \'\074/tr\076\' +\n
            \'\074/tbody\076\' +\n
          \'\074/table\076\');\n
        },\n
        chartCache: [],\n
        chart: function(o) { /* creates a chart for use inside of a cell\n
                                piggybacks RaphealJS\n
                    options:\n
                      type\n
                      data\n
                      legend\n
                      title\n
                      x {data, legend}\n
                      y {data, legend}\n
                              */\n
          function sanitize(v, toNum) {\n
            v = arrHelpers.foldPrepare((v ? v : \'\'), arguments);\n
            if (toNum) {\n
              v = arrHelpers.toNumbers(v);\n
            }\n
            return v;\n
          }\n
          \n
          o = jQuery.extend({\n
            x: { legend: "", data: [0]},\n
            y: { legend: "", data: [0]},\n
            title: "",\n
            data: [0],\n
            legend: "",\n
            chart: jQuery(\'\074div class="\' + jS.cl.chart + \'" /\076\')\n
          }, o);\n
          \n
          o.data = sanitize(o.data, true);\n
          o.x.data = sanitize(o.x.data, true);\n
          o.y.data = sanitize(o.y.data, true);\n
          o.legend = sanitize(o.legend);\n
          o.x.legend = sanitize(o.x.legend);\n
          o.y.legend = sanitize(o.y.legend);\n
          \n
          o.legend = (o.legend ? o.legend : o.data);\n
          \n
          if (Raphael) {\n
            jQuery(document).one(\'calculation\', function() {\n
              var width = o.chart.width();\n
              var height = o.chart.height();\n
              var r = Raphael(o.chart[0]);\n
              if (r.g) {\n
                if (o.title) r.g.text(width / 2, 10, o.title).attr({"font-size": 20});\n
                switch (o.type) {\n
                case "bar":\n
                  r.g.barchart(0, 0, width, height, o.data, o.legend)\n
                    .hover(function () {\n
                      this.flag = r.g.popup(\n
                        this.bar.x,\n
                        this.bar.y,\n
                        this.bar.value || "0"\n
                      ).insertBefore(this);\n
                    },function () {\n
                      this.flag.animate({\n
                        opacity: 0\n
                        },300, \n
                        function () {\n
                          this.remove();\n
                          }\n
                        );\n
                      });\n
                  break;\n
                case "hbar":\n
                  r.g.hbarchart(0, 0, width, height, o.data, o.legend)\n
                    .hover(function () {\n
                      this.flag = r.g.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);\n
                    },function () {\n
                      this.flag.animate({\n
                        opacity: 0\n
                        },300, \n
                        function () {\n
                          this.remove();\n
                          }\n
                        );\n
                      });\n
                  break;\n
                case "line":\n
                  r.g.linechart(width * 0.05, height * 0.03, width * 0.9, height * 0.9, [o.x.data], [o.y.data], {\n
                    nostroke: false, \n
                    axis: "0 0 1 1", \n
                    symbol: "o", \n
                    smooth: true\n
                  })\n
                  .hoverColumn(function () {\n
                    this.tags = r.set();\n
                    for (var i = 0, ii = this.y.length; i \074 ii; i++) {\n
                      this.tags.push(r.g.tag(this.x, this.y[i], this.values[i], 160, 10).insertBefore(this).attr([{fill: "#fff"}, {fill: this.symbols[i].attr("fill")}]));\n
                    }\n
                  }, function () {\n
                    this.tags \046\046 this.tags.remove();\n
                  });\n
                \n
                  break;\n
                case "pie":\n
                  r.g.piechart(width / 2, height / 2, width / 5, o.data, {legend: o.legend})\n
                    .hover(function () {\n
                      this.sector.stop();\n
                      this.sector.scale(1.1, 1.1, this.cx, this.cy);\n
                      if (this.label) {\n
                        this.label[0].stop();\n
                        this.label[0].scale(1.5);\n
                        this.label[1].attr({"font-weight": 800});\n
                      }\n
                    }, function () {\n
                      this.sector.animate({scale: [1, 1, this.cx, this.cy]}, 500, "bounce");\n
                      if (this.label) {\n
                        this.label[0].animate({scale: 1}, 500, "bounce");\n
                        this.label[1].attr({"font-weight": 400});\n
                      }\n
                    });\n
                  break;\n
                case "dot":\n
                  r.g.dotchart(width / 2, height / 2, width / 5, [o.x.data], [o.y.data], [o.data], {\n
                    symbol: "o", \n
                    max: 10, \n
                    heat: true, \n
                    axis: "0 0 1 1", \n
                    axisxstep: legendX.length - 1, \n
                    axisystep: legendY.length - 1, \n
                    axisxlabels: legendX, \n
                    axisxtype: " ", \n
                    axisytype: " ", \n
                    axisylabels: legendY\n
                  })\n
                    .hover(function () {\n
                      this.tag = this.tag || r.g.tag(this.x, this.y, this.value, 0, this.r + 2).insertBefore(this);\n
                      this.tag.show();\n
                    }, function () {\n
                      this.tag \046\046 this.tag.hide();\n
                    });\n
                  break;\n
                }\n
                \n
                jS.attrH.setHeight(jS.getTdLocation(o.chart.parent())[0], \'cell\', false);\n
              }\n
            });\n
          }\n
            \n
          return o.chart;\n
        },\n
        safeImg: function(src, row) { /* creates and image and then resizes the cell\'s row for viewing\n
                        src: string, location of image;\n
                        row: int, the row number where the image is located;\n
                      */\n
          return jQuery(\'\074img /\076\')\n
            .hide()\n
            .load(function() { //prevent the image from being too big for the row\n
              jQuery(this).fadeIn(function() {\n
                jQuery(this).addClass(\'safeImg\');\n
                jS.attrH.setHeight(parseInt(row), \'cell\', false);\n
              });\n
            })\n
            .attr(\'src\', src);\n
        },\n
        inPlaceEdit: function(td) { /* creates a teaxtarea for a user to put a value in that floats on top of the current selected cell\n
                        td: object, the cell to be edited\n
                      */\n
          jS.obj.inPlaceEdit().remove();\n
          var formula = jS.obj.formula();         \n
          var offset = td.offset();\n
          var style = td.attr(\'style\');\n
          var w = td.width();\n
          var h = td.height();\n
          var textarea = jQuery(\'\074textarea id="\' + jS.id.inPlaceEdit + \'" class="\' + jS.cl.inPlaceEdit + \' \' + jS.cl.uiInPlaceEdit + \'" /\076\')\n
            .css(\'left\', offset.left)\n
            .css(\'top\', offset.top)\n
            .width(w)\n
            .height(h)\n
            .keydown(jS.evt.inPlaceEditOnKeyDown)\n
            .keyup(function() {\n
              formula.val(textarea.val());\n
            })\n
            .change(function() {\n
              formula.val(textarea.val());\n
            })\n
            .appendTo(\'body\')\n
            .val(formula.val())\n
            .focus()\n
            .select();\n
          \n
          //Make the textarrea resizable automatically\n
          if (jQuery.fn.elastic) {\n
            textarea.elastic();\n
          }\n
        },\n
        input: { /* inputs for use from the calculations engine */\n
          select: function(v, noBlank) {\n
            var o = jQuery(\'\074select style="width: 100%;" class="clickable" /\076\')\n
              .change(function() {\n
                jS.controlFactory.input.setValue(jQuery(this));\n
              });\n
              \n
            if (!noBlank) {\n
              o.append(\'\074option value=""\076Select a value\074/option\076\');\n
            }\n
              \n
            for (var i = 0; i \074 (v.length \074= 50 ? v.length : 50); i++) {\n
              if (v[i]) {\n
                o.append(\'\074option value="\' + v[i] + \'"\076\' + v[i] + \'\074/option\076\');\n
              }\n
            }\n
            \n
            jQuery(document).one(\'calculation\', function() {\n
              var v = jS.controlFactory.input.getValue(o);\n
              o.val(v);\n
            });\n
            \n
            return o;\n
          },\n
          radio: function(v) {\n
            var radio = jQuery(\'\074span class="clickable" /\076\');\n
            for (var i = 0; i \074 (v.length \074= 25 ? v.length : 25); i++) {\n
              if (v[i]) {\n
                radio\n
                  .append(\n
                    jQuery(\'\074input type="radio" name="\' + name + \'" /\076\')\n
                      .val(v[i])\n
                      .change(function() {\n
                        radio.find(\'input\').removeAttr(\'CHECKED\');\n
                        jQuery(this).attr(\'CHECKED\', true);\n
                        jS.controlFactory.input.setValue(jQuery(this), radio.parent());\n
                      })\n
                  )\n
                  .append(\'\074span class="clickable"\076\' + v[i] + \'\074/span\076\')\n
                  .append(\'\074br /\076\');\n
              }\n
            }\n
            \n
            jQuery(document).one(\'calculation\', function() {\n
              radio.find(\'input\')\n
                .attr(\'name\', radio.parent().attr(\'id\') + \'_radio\');\n
              var val = jS.controlFactory.input.getValue(radio);\n
              radio.find(\'input[value="\' + val + \'"]\')\n
                .attr(\'CHECKED\', true);\n
            });\n
            \n
            return radio;\n
          },\n
          checkbox: function(v) {\n
            var o = jQuery(\'\074span class="clickable" /\076\')\n
              .append(\n
                jQuery(\'\074input type="checkbox" /\076\')\n
                  .val(v)\n
                  .change(function() {\n
                    o.parent().removeAttr(\'selectedvalue\');\n
                    if (jQuery(this).is(\':checked\')) {\n
                      jS.controlFactory.input.setValue(jQuery(this), o.parent());\n
                    }\n
                    jS.calc();\n
                  })\n
              )\n
              .append(\'\074span\076\' + v + \'\074/span\076\074br /\076\');\n
              \n
            jQuery(document).one(\'calculation\', function() {\n
              o.find(\'input\').removeAttr(\'CHECKED\');\n
              o.find(\'input[value="\' + o.parent().attr(\'selectedvalue\') + \'"]\').attr(\'CHECKED\', \'TRUE\');\n
            });\n
            return o;\n
          },\n
          setValue: function(o, parent) {\n
            jQuery(parent ? parent : o.parent()).attr(\'selectedvalue\', o.val());;\n
            jS.calc();\n
          },\n
          getValue: function(o, parent) {\n
            return jQuery(parent ? parent : o.parent()).attr(\'selectedvalue\');\n
          }\n
        },\n
        autoFiller: function() { /* created the autofiller object */\n
          return jQuery(\'\074div id="\' + (jS.id.autoFiller + jS.i) + \'" class="\' + jS.cl.autoFiller + \' \' + jS.cl.uiAutoFiller + \'"\076\' +\n
                  \'\074div class="\' + jS.cl.autoFillerHandle + \'" /\076\' +\n
                  \'\074div class="\' + jS.cl.autoFillerCover + \'" /\076\' +\n
              \'\074/div\076\')\n
              .mousedown(function(e) {\n
                var td = jS.cellLast.td;\n
                if (td) {\n
                  var loc = jS.getTdLocation(td);\n
                  jS.cellSetActive(td, loc, true, jS.autoFillerNotGroup, function() {                   \n
                    jS.fillUpOrDown();\n
                    jS.autoFillerGoToTd(jS.obj.cellHighlighted().last());\n
                    jS.autoFillerNotGroup = false;\n
                  });\n
                }\n
              });\n
        }\n
      },\n
      autoFillerNotGroup: true,\n
      sizeSync: { /* future location of all deminsion sync/mods */\n
      \n
      },\n
      evt: { /* event handlers for sheet; e = event */\n
        keyDownHandler: {\n
          enterOnInPlaceEdit: function(e) {\n
            if (!e.shiftKey) {\n
              return jS.evt.cellSetFocusFromKeyCode(e);\n
            } else {\n
              return true;\n
            }\n
          },\n
          enter: function(e) {\n
            if (!jS.cellLast.isEdit \046\046 !e.ctrlKey) {\n
              jS.cellLast.td.dblclick();\n
              return false;\n
            } else {\n
              return this.enterOnInPlaceEdit(e);\n
            }\n
          },\n
          tab: function(e) {\n
            return jS.evt.cellSetFocusFromKeyCode(e);\n
          },\n
          pasteOverCells: function(e) { //used for pasting from other spreadsheets\n
            if (e.ctrlKey) {\n
              var formula = jS.obj.formula(); //so we don\'t have to keep calling the function and wasting memory\n
              var oldVal = formula.val();\n
              formula.val(\'\');  //we use formula to catch the pasted data\n
              var newValCount = 0;\n
              \n
              jQuery(document).one(\'keyup\', function() {\n
                var loc = jS.getTdLocation(jS.cellLast.td); //save the currrent cell\n
                var val = formula.val(); //once ctrl+v is hit formula now has the data we need\n
                var firstValue = \'\';\n
                formula.val(\'\'); \n
                var tdsBefore = jQuery(\'\074div /\076\');\n
                var tdsAfter = jQuery(\'\074div /\076\');\n
                \n
                var row = val.split(/\\n/g); //break at rows\n
                \n
                for (var i = 0; i \074 row.length; i++) {\n
                  var col = row[i].split(/\\t/g); //break at columns\n
                  for (var j = 0; j \074 col.length; j++) {\n
                    newValCount++;\n
                    if (col[j]) {\n
                      var td = jQuery(jS.getTd(jS.i, i + loc[0], j + loc[1]));\n
                      \n
                      tdsBefore.append(td.clone());\n
                      \n
                      \n
                      if ((col[j] + \'\').charAt(0) == \'=\') { //we need to know if it\'s a formula here\n
                        td.attr(\'formula\', col[j]);\n
                      } else {\n
                        td\n
                          .html(col[j])\n
                          .removeAttr(\'formula\'); //we get rid of formula because we don\'t know if it was a formula, to check may take too long\n
                      }\n
                      \n
                      tdsAfter.append(td.clone());\n
                      \n
                      if (i == 0 \046\046 j == 0) { //we have to finish the current edit\n
                        firstValue = col[j];\n
                      }\n
                    }\n
                  }\n
                }\n
                \n
                jS.cellUndoable.add(tdsBefore.children());\n
                jS.cellUndoable.add(tdsAfter.children());\n
                \n
                formula.val(firstValue);\n
                \n
                if (newValCount == 1) {//minimum is 2 for index of 1x1\n
                  jS.fillUpOrDown(false, false, firstValue);\n
                }\n
                \n
                jS.setDirty(true);\n
                jS.evt.cellEditDone(true);\n
              });\n
            }\n
            jS.calc();\n
            return true;\n
          },\n
          findCell: function(e) {\n
            if (e.ctrlKey) { \n
              jS.cellFind();\n
              return false;\n
            }\n
            return true;\n
          },\n
          redo: function(e) {\n
            if (e.ctrlKey \046\046 !jS.cellLast.isEdit) { \n
              jS.cellUndoable.undoOrRedo();\n
              return false;\n
            }\n
            return true;\n
          },\n
          undo: function(e) {\n
            if (e.ctrlKey \046\046 !jS.cellLast.isEdit) {\n
              jS.cellUndoable.undoOrRedo(true);\n
              return false;\n
            }\n
            return true;\n
          },\n
          pageUpDown: function(reverse) {\n
            var pane = jS.obj.pane();\n
            var left = jS.cellLast.td.position().left;\n
            var top = 0;\n
            \n
            if (reverse) {\n
              top = 0;\n
              pane.scrollTop(pane.scrollTop() - pane.height());\n
              \n
            } else {\n
              top = pane.height() - (s.colMargin * 3);\n
              pane.scrollTop(pane.scrollTop() + top);\n
            }\n
            \n
            return jS.evt.cellSetFocusFromXY(left, top);\n
          },\n
          formulaOnKeyDown: function(e) {\n
            switch (e.keyCode) {\n
              case key.ESCAPE:  jS.evt.cellEditAbandon();\n
                break;\n
              case key.TAB:     return jS.evt.keyDownHandler.tab(e);\n
                break;\n
              case key.ENTER:   return jS.evt.keyDownHandler.enter(e);\n
                break;\n
              case key.LEFT:\n
              case key.UP:\n
              case key.RIGHT:\n
              case key.DOWN:    return jS.evt.cellSetFocusFromKeyCode(e);\n
                break;\n
              case key.PAGE_UP: return jS.evt.keyDownHandler.pageUpDown(true);\n
                break;\n
              case key.PAGE_DOWN: return jS.evt.keyDownHandler.pageUpDown();\n
                break;\n
              case key.V:     return jS.evt.keyDownHandler.pasteOverCells(e);\n
                break;\n
              case key.Y:     return jS.evt.keyDownHandler.redo(e);\n
                break;\n
              case key.Z:     return jS.evt.keyDownHandler.undo(e);\n
                break;\n
              case key.F:     return jS.evt.keyDownHandler.findCell(e);\n
              case key.CONTROL: //we need to filter these to keep cell state\n
              case key.CAPS_LOCK:\n
              case key.SHIFT:\n
              case key.ALT:\n
              case key.UP:\n
              case key.DOWN:\n
              case key.LEFT:\n
              case key.RIGHT:\n
                break;\n
              case key.HOME:\n
              case key.END:   jS.evt.cellSetFocusFromKeyCode(e);\n
                break;\n
              default:      jS.cellLast.isEdit = true;\n
            }\n
          }\n
        },\n
        inPlaceEditOnKeyDown: function(e) {\n
          switch (e.keyCode) {\n
            case key.ENTER:   return jS.evt.keyDownHandler.enterOnInPlaceEdit(e);\n
              break;\n
            case key.TAB:     return jS.evt.keyDownHandler.tab(e);\n
              break;\n
            case key.ESCAPE:  jS.evt.cellEditAbandon(); return false;\n
              break;\n
          }\n
        },\n
        formulaChange: function(e) {\n
          jS.obj.inPlaceEdit().val(jS.obj.formula().val());\n
        },\n
        inPlaceEditChange: function(e) {\n
          jS.obj.formula().val(jS.obj.inPlaceEdit().val());\n
        },\n
        cellEditDone: function(forceCalc) { /* called to edit a cells value from jS.obj.formula(), afterward setting "fnAfterCellEdit" is called w/ params (td, row, col, spreadsheetIndex, sheetIndex)\n
                            forceCalc: bool, if set to true forces a calculation of the selected sheet\n
                          */\n
          switch (jS.cellLast.isEdit) {\n
            case true:\n
              jS.obj.inPlaceEdit().remove();\n
              var formula = jS.obj.formula();\n
              formula.unbind(\'keydown\'); //remove any lingering events from inPlaceEdit\n
              var td = jS.cellLast.td;\n
              \n
              switch(jS.isFormulaEditable(td)) {\n
                case true:\n
                  //Lets ensure that the cell being edited is actually active\n
                  if (td) { \n
                    //first, let\'s make it undoable before we edit it\n
                    jS.cellUndoable.add(td);\n
                    \n
                    //This should return either a val from textbox or formula, but if fails it tries once more from formula.\n
                    var v = jS.manageTextToHtml(formula.val());\n
                    var prevVal = td.html();\n
\n
                    if (v.charAt(0) == \'=\') {\n
                      td\n
                        .attr(\'formula\', v)\n
                        .html(\'\');\n
                    } else {\n
                      td\n
                        .removeAttr(\'formula\')\n
                        .html(v);\n
                    }\n
                    \n
                    if (v != prevVal || forceCalc) {\n
                      jS.calc();\n
                    }\n
                    \n
                    jS.attrH.setHeight(jS.cellLast.row, \'cell\');\n
                    \n
                    //Save the newest version of that cell\n
                    jS.cellUndoable.add(td);\n
                    \n
                    formula.focus().select();\n
                    jS.cellLast.isEdit = false;\n
                    \n
                    jS.setDirty(true);\n
                    \n
                    //perform final function call\n
                    s.fnAfterCellEdit({\n
                      td: jS.cellLast.td,\n
                      row: jS.cellLast.row,\n
                      col: jS.cellLast.col,\n
                      spreadsheetIndex: jS.i,\n
                      sheetIndex: I\n
                    });\n
                  }\n
              }\n
              break;\n
            default:\n
              jS.attrH.setHeight(jS.cellLast.row, \'cell\', false);\n
          }\n
        },\n
        cellEditAbandon: function(skipCalc) { /* removes focus of a selected cell and doesn\'t change it\'s value\n
                              skipCalc: bool, if set to true will skip sheet calculation;\n
                            */\n
          jS.obj.inPlaceEdit().remove();\n
          jS.themeRoller.cell.clearActive();\n
          jS.themeRoller.bar.clearActive();\n
          jS.themeRoller.cell.clearHighlighted();\n
          \n
          if (!skipCalc) {\n
            jS.calc();\n
          }\n
          \n
          jS.cellLast.td = jQuery(\'\074td /\076\');\n
          jS.cellLast.row = jS.cellLast.col = -1;\n
          jS.rowLast = jS.colLast = -1;\n
          \n
          jS.labelUpdate(\'\', true);\n
          jS.obj.formula()\n
            .val(\'\');\n
          \n
          if (s.autoFiller) {\n
            jS.obj.autoFiller().hide();\n
          }\n
          \n
          return false;\n
        },\n
        cellSetFocusFromXY: function(left, top, skipOffset) { /* a handy function the will set a cell active by it\'s location on the browser;\n
                                    left: int, pixels left;\n
                                    top: int, pixels top;\n
                                    skipOffset: bool, skips offset;\n
                                  */\n
          var td = jS.getTdFromXY(left, top, skipOffset);\n
          \n
          if (jS.isTd(td)) {\n
            jS.themeRoller.cell.clearHighlighted();\n
            \n
            jS.cellEdit(td);\n
            return false;\n
          } else {\n
            return true;\n
          }\n
        },\n
        cellSetFocusFromKeyCode: function(e) { /* invoke a click on next/prev cell */\n
          var c = jS.cellLast.col; //we don\'t set the cellLast.col here so that we never go into indexes that don\'t exist\n
          var r = jS.cellLast.row;\n
          var overrideIsEdit = false;\n
          \n
          switch (e.keyCode) {\n
            case key.UP:    r--; break;\n
            case key.DOWN:    r++; break;\n
            case key.LEFT:    c--; break;\n
            case key.RIGHT:   c++; break;\n
            case key.ENTER:   r++;\n
              overrideIsEdit = true;\n
              if (s.autoAddCells) {\n
                if (jS.cellLast.row == jS.sheetSize()[0]) {\n
                  jS.controlFactory.addRow(\':last\');\n
                }\n
              }\n
              break;\n
            case key.TAB:\n
              overrideIsEdit = true;\n
              if (e.shiftKey) {\n
                c--;\n
              } else {\n
                c++;\n
              }\n
              if (s.autoAddCells) {\n
                if (jS.cellLast.col == jS.sheetSize()[1]) {\n
                  jS.controlFactory.addColumn(\':last\');\n
                }\n
              }\n
              break;\n
            case key.HOME:    c = 0; break;\n
            case key.END:   c = jS.cellLast.td.parent().find(\'td\').length - 1; break;\n
          }\n
          \n
          //we check here and make sure all values are above -1, so that we get a selected cell\n
          c = (c \074 0 ? 0 : c);\n
          r = (r \074 0 ? 0 : r);\n
          \n
          //to get the td could possibly make keystrokes slow, we prevent it here so the user doesn\'t even know we are listening ;)\n
          if (!jS.cellLast.isEdit || overrideIsEdit) {\n
            //get the td that we want to go to\n
            var td = jS.getTd(jS.i, r, c);\n
          \n
            //if the td exists, lets go to it\n
            if (td) {\n
              jS.themeRoller.cell.clearHighlighted();\n
              jS.cellEdit(jQuery(td));\n
              return false;\n
            }\n
          }\n
          \n
          //default, can be overridden above\n
          return true;\n
        },\n
        cellOnMouseDown: function(e) {\n
          if (e.shiftKey) {\n
            jS.getTdRange(e, jS.obj.formula().val());\n
          } else {\n
            jS.cellEdit(jQuery(e.target), true);\n
          }     \n
        },\n
        cellOnDblClick: function(e) {\n
          jS.cellLast.isEdit = jS.isSheetEdit = true;\n
          jS.controlFactory.inPlaceEdit(jS.cellLast.td);\n
          jS.log(\'click, in place edit activated\');\n
        },\n
        tabOnMouseDown: function(e) {\n
          var i = jQuery(e.target).attr(\'i\');\n
          \n
          if (i != \'-1\' \046\046 i != jS.i) {\n
            jS.setActiveSheet(i);\n
            jS.calc(i);\n
          } else if (i != \'-1\' \046\046 jS.i == i) {\n
            jS.sheetTab();\n
          } else {\n
            jS.addSheet(\'5x10\');\n
          }\n
          \n
          s.fnSwitchSheet(i);\n
          return false;\n
        },\n
        resizeBar: function(e, o) {\n
          //Resize Column \046 Row \046 Prototype functions are private under class jSheet    \n
          var target = jQuery(e.target);\n
          var resizeBar = {\n
            start: function(e) {\n
              \n
              jS.log(\'start resize\');\n
              //I never had any problems with the numbers not being ints but I used the parse method\n
              //to ensuev non-breakage\n
              o.offset = target.offset();\n
              o.tdPageXY = [o.offset.left, o.offset.top][o.xyDimension];\n
              o.startXY = [e.pageX, e.pageY][o.xyDimension];\n
              o.i = o.getIndex(target);\n
              o.srcBarSize = o.getSize(target);\n
              o.edgeDelta = o.startXY - (o.tdPageXY + o.srcBarSize);\n
              o.min = 10;\n
              \n
              if (s.joinedResizing) {\n
                o.resizeFn = function(size) {\n
                  o.setDesinationSize(size);\n
                  o.setSize(target, size);\n
                };\n
              } else {\n
                o.resizeFn = function(size) {\n
                  o.setSize(target, size);\n
                };\n
              }\n
              \n
              //We start the drag sequence\n
              if (Math.abs(o.edgeDelta) \074= o.min) {\n
                //some ui enhancements, lets the user know he\'s resizing\n
                jQuery(e.target).parent().css(\'cursor\', o.cursor);\n
                \n
                jQuery(document)\n
                  .mousemove(resizeBar.drag)\n
                  .mouseup(resizeBar.stop);\n
                \n
                return true; //is resizing\n
              } else {\n
                return false; //isn\'t resizing\n
              }\n
            },\n
            drag: function(e) {\n
              var newSize = o.min;\n
\n
              var v = o.srcBarSize + ([e.pageX, e.pageY][o.xyDimension] - o.startXY);\n
              if (v \076 0) {// A non-zero minimum size saves many headaches.\n
                newSize = Math.max(v, o.min);\n
              }\n
\n
              o.resizeFn(newSize);\n
              return false;\n
            },\n
            stop: function(e) {\n
              o.setDesinationSize(o.getSize(target));\n
              \n
              jQuery(document)\n
                .unbind(\'mousemove\')\n
                .unbind(\'mouseup\');\n
\n
              jS.obj.formula()\n
                .focus()\n
                .select();\n
              \n
              target.parent().css(\'cursor\', \'pointer\');\n
              \n
              jS.autoFillerGoToTd();\n
              \n
              jS.log(\'stop resizing\');\n
            }\n
          };\n
          \n
          return resizeBar.start(e);\n
        },\n
        scrollBars: function(pane) { /* makes the bars scroll as the sheet is scrolled\n
                        pane: object, the sheet\'s pane;\n
                      */\n
          var o = { //cut down on recursion, grab them once\n
            barLeft: jS.obj.barLeftParent(), \n
            barTop: jS.obj.barTopParent()\n
          };\n
          \n
          pane.scroll(function() {\n
            o.barTop.scrollLeft(pane.scrollLeft());//2 lines of beautiful jQuery js\n
            o.barLeft.scrollTop(pane.scrollTop());\n
            \n
            s.fnPaneScroll(pane, jS.i);\n
          });\n
        },\n
        barMouseDown: { /* handles bar events, including resizing */\n
          select: function(o, e, selectFn, resizeFn) {\n
            var isResizing = jS.evt.resizeBar(e, resizeFn);\n
                \n
            if (!isResizing) {\n
              selectFn(e.target);\n
              o\n
                .unbind(\'mouseover\')\n
                .mouseover(function(e) {\n
                  selectFn(e.target);\n
                });\n
                \n
              jQuery(document)\n
                .one(\'mouseup\', function() {\n
                  o\n
                    .unbind(\'mouseover\')\n
                    .unbind(\'mouseup\');\n
                });\n
            }\n
            \n
            return false;\n
          },\n
          first: 0,\n
          last: 0,\n
          height: function(o) {     \n
            var selectRow = function () {};\n
            \n
            o //let any user resize\n
              .unbind(\'mousedown\')\n
              .mousedown(function(e) {\n
                if (!jQuery(e.target).hasClass(jS.cl.barLeft)) {\n
                  jS.evt.barMouseDown.first = jS.evt.barMouseDown.last = jS.rowLast = jS.getBarLeftIndex(e.target);\n
                  jS.evt.barMouseDown.select(o, e, selectRow, jS.rowResizer);\n
                }\n
                return false;\n
              });\n
            if (s.editable) { //only let editable select\n
              selectRow = function(o) {\n
                if (!jQuery(o).attr(\'id\')) {\n
                  var i = jS.getBarLeftIndex(o);\n
                  \n
                  jS.rowLast = i; //keep track of last row for inserting new rows\n
                  jS.evt.barMouseDown.last = i;\n
                  \n
                  jS.cellSetActiveBar(\'row\', jS.evt.barMouseDown.first, jS.evt.barMouseDown.last);\n
                }\n
              };\n
            }\n
          },\n
          width: function(o) {\n
            var selectColumn = function() {};\n
            \n
            o //let any user resize\n
              .unbind(\'mousedown\')\n
              .mousedown(function(e) {\n
                if (!jQuery(e.target).hasClass(jS.cl.barTop)) {\n
                  jS.evt.barMouseDown.first = jS.evt.barMouseDown.last = jS.colLast = jS.getBarTopIndex(e.target);\n
                  jS.evt.barMouseDown.select(o, e, selectColumn, jS.columnResizer);\n
                }\n
                \n
                return false;\n
              });\n
            if (s.editable) { //only let editable select\n
              selectColumn = function(o) {\n
                if (!jQuery(o).attr(\'id\')) {\n
                  var i = jS.getBarTopIndex(o);\n
                  \n
                  jS.colLast = i; //keep track of last column for inserting new columns\n
                  jS.evt.barMouseDown.last = i;\n
                  \n
                  jS.cellSetActiveBar(\'col\', jS.evt.barMouseDown.first, jS.evt.barMouseDown.last);\n
                }\n
              };\n
            }\n
          }\n
        }\n
      },\n
      isTd: function(o) { /* ensures the the object selected is actually a td that is in a sheet\n
                  o: object, cell object;\n
                */\n
        o = (o[0] ? o[0] : [o]);\n
        if (o[0]) {\n
          if (!isNaN(o[0].cellIndex)) { \n
            return true;\n
          }\n
        }\n
        return false;\n
      },\n
      isFormulaEditable: function(o) { /* ensures that formula attribute of an object is editable\n
                          o: object, td object being used as cell\n
                      */\n
        if (s.lockFormulas) {\n
          if(o.attr(\'formula\') !== undefined) {\n
            return false;\n
          }\n
        }\n
        return true;\n
      },\n
      toggleFullScreen: function() { /* toggles full screen mode */\n
        if (jS.obj.fullScreen().is(\':visible\')) { //here we remove full screen\n
          jQuery(\'body\').removeClass(\'bodyNoScroll\');\n
          s.parent = origParent;\n
          \n
          var w = s.parent.width();\n
          var h = s.parent.height();\n
          s.width = w;\n
          s.height = h;\n
          \n
          jS.obj.tabContainer().insertAfter(\n
            s.parent.append(jS.obj.fullScreen().children())\n
          ).removeClass(jS.cl.tabContainerFullScreen);\n
          \n
          jS.obj.fullScreen().remove();\n
          \n
          jS.sheetSyncSize();\n
        } else { //here we make a full screen\n
          jQuery(\'body\').addClass(\'bodyNoScroll\');\n
          \n
          var w = $window.width() - 15;\n
          var h = $window.height() - 35;\n
          \n
          \n
          s.width = w;\n
          s.height = h;\n
          \n
          jS.obj.tabContainer().insertAfter(\n
            jQuery(\'\074div class="\' + jS.cl.fullScreen + \' \' + jS.cl.uiFullScreen + \'" /\076\')\n
              .append(s.parent.children())\n
              .appendTo(\'body\')\n
          ).addClass(jS.cl.tabContainerFullScreen);\n
          \n
          s.parent = jS.obj.fullScreen();\n
          \n
          jS.sheetSyncSize();\n
        }\n
      },\n
      tuneTableForSheetUse: function(o) { /* makes table object usable by sheet\n
                          o: object, table object;\n
                        */\n
        o\n
          .addClass(jS.cl.sheet)\n
          .attr(\'id\', jS.id.sheet + jS.i)\n
          .attr(\'border\', \'1px\')\n
          .attr(\'cellpadding\', \'0\')\n
          .attr(\'cellspacing\', \'0\');\n
          \n
        o.find(\'td.\' + jS.cl.cellActive).removeClass(jS.cl.cellActive);\n
        \n
        return o;\n
      },\n
      attrH: {/* Attribute Helpers\n
            I created this object so I could see, quickly, which attribute was most stable.\n
            As it turns out, all browsers are different, thus this has evolved to a much uglier beast\n
          */\n
        width: function(o, skipCorrection) {\n
          return jQuery(o).outerWidth() - (skipCorrection ? 0 : s.boxModelCorrection);\n
        },\n
        widthReverse: function(o, skipCorrection) {\n
          return jQuery(o).outerWidth() + (skipCorrection ? 0 : s.boxModelCorrection);\n
        },\n
        height: function(o, skipCorrection) {\n
          return jQuery(o).outerHeight() - (skipCorrection ? 0 : s.boxModelCorrection);\n
        },\n
        heightReverse: function(o, skipCorrection) {\n
          return jQuery(o).outerHeight() + (skipCorrection ? 0 : s.boxModelCorrection);\n
        },\n
        syncSheetWidthFromTds: function(o) {\n
          var w = 0;\n
          o = (o ? o : jS.obj.sheet());\n
          o.find(\'col\').each(function() {\n
            w += jQuery(this).width();\n
          });\n
          o.width(w);\n
          return w;\n
        },\n
        setHeight: function(i, from, skipCorrection, o) {\n
          var correction = 0;\n
          var h = 0;\n
          var fn;\n
          \n
          switch(from) {\n
            case \'cell\':\n
              o = (o ? o : jS.obj.barLeft().find(\'div\').eq(i));\n
              h = jS.attrH.height(jQuery(jS.getTd(jS.i, i, 0)).parent().andSelf(), skipCorrection);\n
              break;\n
            case \'bar\':\n
              if (!o) {\n
                var tr = jQuery(jS.getTd(jS.i, i, 0)).parent();\n
                var td = tr.children();\n
                o = tr.add(td);\n
              } \n
              h = jS.attrH.heightReverse(jS.obj.barLeft().find(\'div\').eq(i), skipCorrection);\n
              break;\n
          }\n
          \n
          if (h) {\n
            jQuery(o)\n
              .height(h)\n
              .css(\'height\', h + \'px\')\n
              .attr(\'height\', h + \'px\');\n
          }\n
\n
          return o;\n
        }\n
      },\n
      setTdIds: function(o) { /* cycles through all the td in a sheet and sets their id so it can be quickly referenced later\n
                    o: object, cell object;\n
                  */\n
        o = (o ? o : jS.obj.sheet());\n
        o.find(\'tr\').each(function(row) {\n
          jQuery(this).find(\'td,th\').each(function(col) {\n
            jQuery(this).attr(\'id\', jS.getTdId(jS.i, row, col));\n
          });\n
        });\n
      },\n
      setControlIds: function() { /* resets the control ids, useful for when adding new sheets/controls between sheets/controls :) */\n
        var resetIds = function(o, id) {\n
          o.each(function(i) {\n
            jQuery(this).attr(\'id\', id + i);\n
          });\n
        };\n
        \n
        resetIds(jS.obj.sheetAll().each(function() {\n
          jS.setTdIds(jQuery(this));\n
        }), jS.id.sheet);\n
        \n
        resetIds(jS.obj.barTopAll(), jS.id.barTop);\n
        resetIds(jS.obj.barTopParentAll(), jS.id.barTopParent);\n
        resetIds(jS.obj.barLeftAll(), jS.id.barLeft);\n
        resetIds(jS.obj.barLeftParentAll(), jS.id.barLeftParent);\n
        resetIds(jS.obj.barCornerAll(), jS.id.barCorner);\n
        resetIds(jS.obj.barCornerParentAll(), jS.id.barCornerParent);\n
        resetIds(jS.obj.tableControlAll(), jS.id.tableControl);\n
        resetIds(jS.obj.paneAll(), jS.id.pane);\n
        resetIds(jS.obj.tabAll().each(function(j) {\n
          jQuery(this).attr(\'i\', j);\n
        }), jS.id.tab);\n
      },\n
      columnResizer: { /* used for resizing columns */\n
        xyDimension: 0,\n
        getIndex: function(o) {\n
          return jS.getBarTopIndex(o);\n
        },\n
        getSize: function(o) {\n
          return jS.attrH.width(o, true);\n
        },\n
        setSize: function(o, v) {\n
          o.width(v);\n
        },\n
        setDesinationSize: function(w) {\n
          jS.sheetSyncSizeToDivs();\n
          \n
          jS.obj.sheet().find(\'col\').eq(this.i)\n
            .width(w)\n
            .css(\'width\', w)\n
            .attr(\'width\', w);\n
          \n
          jS.obj.pane().scroll();\n
        },\n
        cursor: \'w-resize\'\n
      },\n
      rowResizer: { /* used for resizing rows */\n
        xyDimension: 1,\n
          getIndex: function(o) {\n
            return jS.getBarLeftIndex(o);\n
          },\n
          getSize: function(o) {\n
            return jS.attrH.height(o, true);\n
          },\n
          setSize: function(o, v) {\n
            if (v) {\n
            o\n
              .height(v)\n
              .css(\'height\', v)\n
              .attr(\'height\', v);\n
            }\n
            return jS.attrH.height(o);\n
          },\n
          setDesinationSize: function() {\n
            //Set the cell height\n
            jS.attrH.setHeight(this.i, \'bar\', true);\n
            \n
            //Reset the bar height if the resized row don\'t match\n
            jS.attrH.setHeight(this.i, \'cell\', false);\n
            \n
            jS.obj.pane().scroll();\n
          },\n
          cursor: \'s-resize\'\n
      },\n
      toggleHide: {//These are not ready for prime time\n
        row: function(i) {\n
          if (!i) {//If i is empty, lets get the current row\n
            i = jS.obj.cellActive().parent().attr(\'rowIndex\');\n
          }\n
          if (i) {//Make sure that i equals something\n
            var o = jS.obj.barLeft().find(\'div\').eq(i);\n
            if (o.is(\':visible\')) {//This hides the current row\n
              o.hide();\n
              jS.obj.sheet().find(\'tr\').eq(i).hide();\n
            } else {//This unhides\n
              //This unhides the currently selected row\n
              o.show();\n
              jS.obj.sheet().find(\'tr\').eq(i).show();\n
            }\n
          } else {\n
            alert(jS.msg.toggleHideRow);\n
          }\n
        },\n
        rowAll: function() {\n
          jS.obj.sheet().find(\'tr\').show();\n
          jS.obj.barLeft().find(\'div\').show();\n
        },\n
        column: function(i) {\n
          if (!i) {\n
            i = jS.obj.cellActive().attr(\'cellIndex\');\n
          }\n
          if (i) {\n
            //We need to hide both the col and td of the same i\n
            var o = jS.obj.barTop().find(\'div\').eq(i);\n
            if (o.is(\':visible\')) {\n
              jS.obj.sheet().find(\'tbody tr\').each(function() {\n
                jQuery(this).find(\'td,th\').eq(i).hide();\n
              });\n
              o.hide();\n
              jS.obj.sheet().find(\'colgroup col\').eq(i).hide();\n
              jS.toggleHide.columnSizeManage();\n
            }\n
          } else {\n
            alert(jS.msg.toggleHideColumn);\n
          }\n
        },\n
        columnAll: function() {\n
        \n
        },\n
        columnSizeManage: function() {\n
          var w = jS.obj.barTop().width();\n
          var newW = 0;\n
          var newW = 0;\n
          jS.obj.barTop().find(\'div\').each(function() {\n
            var o = jQuery(this);\n
            if (o.is(\':hidden\')) {\n
              newW += o.width();\n
            }\n
          });\n
          jS.obj.barTop().width(w);\n
          jS.obj.sheet().width(w);\n
        }\n
      },\n
      merge: function() { /* merges cells */\n
        var cellsValue = "";\n
        var cellValue = "";\n
        var cells = jS.obj.cellHighlighted();\n
        var formula;\n
        var cellFirstLoc = jS.getTdLocation(cells.first());\n
        var cellLastLoc = jS.getTdLocation(cells.last());\n
        var colI = (cellLastLoc[1] - cellFirstLoc[1]) + 1;\n
        \n
        if (cells.length \076 1 \046\046 cellFirstLoc[0]) {\n
          for (var i = cellFirstLoc[1]; i \074= cellLastLoc[1]; i++) {\n
            var cell = jQuery(jS.getTd(jS.i, cellFirstLoc[0], i)).hide();\n
            formula = cell.attr(\'formula\');\n
            cellValue = cell.html();\n
            \n
            cellValue = (cellValue ? cellValue + \' \' : \'\');\n
            \n
            cellsValue = (formula ? "(" + formula.replace(\'=\', \'\') + ")" : cellValue) + cellsValue;\n
            \n
            if (i != cellFirstLoc[1]) {\n
              cell\n
                .attr(\'formula\', \'\')\n
                .html(\'\')\n
                .hide();\n
            }\n
          }\n
          \n
          var cell = cells.first()\n
            .show()\n
            .attr(\'colspan\', colI)\n
            .html(cellsValue);\n
          \n
          jS.setDirty(true);\n
          jS.calc();\n
        } else if (!cellFirstLoc[0]) {\n
          alert(jS.msg.merge);\n
        }\n
      },\n
      unmerge: function() { /* unmerges cells */\n
        var cell = jS.obj.cellHighlighted().first();\n
        var loc = jS.getTdLocation(cell);\n
        var formula = cell.attr(\'formula\');\n
        var v = cell.html();\n
        v = (formula ? formula : v);\n
        \n
        var rowI = cell.attr(\'rowspan\');\n
        var colI = cell.attr(\'colspan\');\n
        \n
        //rowI = parseInt(rowI ? rowI : 1); //we have to have a minimum here;\n
        colI = parseInt(colI ? colI : 1);\n
        \n
        var td = \'\074td /\076\';\n
        \n
        var tds = \'\';\n
        \n
        if (colI) {\n
          for (var i = 0; i \074 colI; i++) {\n
            tds += td;\n
          }\n
        }\n
        \n
        for (var i = loc[1]; i \074 colI; i++) {\n
          jQuery(jS.getTd(jS.i, loc[0], i)).show();\n
        }\n
        \n
        cell.removeAttr(\'colspan\');\n
        \n
        jS.setDirty(true);\n
        jS.calc();\n
      },\n
      fillUpOrDown: function(goUp, skipOffsetForumals, v) { /* fills values down or up to highlighted cells from active cell;\n
                                  goUp: bool, default is down, when set to true value are filled from bottom, up;\n
                                  skipOffsetForumals: bool, default is formulas will offest, when set to true formulas will stay static;\n
                                  v: string, the value to set cells to, if not set, formula will be used;\n
                                */\n
        var cells = jS.obj.cellHighlighted();\n
        var cellActive = jS.obj.cellActive();\n
        //Make it undoable\n
        jS.cellUndoable.add(cells);\n
        \n
        var startFromActiveCell = cellActive.hasClass(jS.cl.uiCellHighlighted);\n
        var locFirst = jS.getTdLocation(cells.first());\n
        var locLast = jS.getTdLocation(cells.last());\n
        \n
        v = (v ? v : jS.obj.formula().val()); //allow value to be overridden\n
        \n
        var fn;\n
        \n
        var formulaOffset = (startFromActiveCell ? 0 : 1);\n
        \n
        if ((v + \'\').charAt(0) == \'=\') {\n
          fn = function(o, i) {\n
            o\n
              .attr(\'formula\', (skipOffsetForumals ? v : jS.offsetFormula(v, i + formulaOffset, 0)))\n
              .html(\'\'); //we subtract one here because cells are 1 based and indexes are 0 based\n
          };\n
        } else {\n
          fn = function (o) {\n
            o\n
              .removeAttr(\'formula\')\n
              .html(v);\n
          };\n
        }\n
        \n
        function fill(r, c, i) {\n
          var td = jQuery(jS.getTd(jS.i, r, c));\n
          \n
          //make sure the formula isn\'t locked for this cell\n
          if (jS.isFormulaEditable(td)) {\n
            fn(td, i);\n
          }\n
        }\n
        \n
        var k = 0;\n
        if (goUp) {\n
          for (var i = locLast[0]; i \076= locFirst[0]; i--) {\n
            for (var j = locLast[1]; j \076= locFirst[1]; j--) {\n
              fill(i, j, k);\n
              k++;\n
            }\n
          }\n
        } else {\n
          for (var i = locFirst[0]; i \074= locLast[0]; i++) {\n
            for (var j = locFirst[1]; j \074= locLast[1]; j++) {\n
              fill(i, j, k);\n
              k++;\n
            }\n
          }\n
        }\n
        \n
        jS.setDirty(true);\n
        jS.calc();\n
        \n
        //Make it redoable\n
        jS.cellUndoable.add(cells);\n
      },\n
      offsetFormulaRange: function(row, col, rowOffset, colOffset, isBefore) {/* makes cell formulas increment in a range\n
                                            row: int;\n
                                            col: int;\n
                                            rowOffset: int, offsets row increment;\n
                                            colOffset: int, offsets col increment;\n
                                            isBefore: bool, makes increment backward;\n
                                          */\n
        var shiftedRange = {\n
          first: [(row ? row : 0), (col ? col : 0)],\n
          last: jS.sheetSize()\n
        };\n
        \n
        if (!isBefore \046\046 rowOffset) { //this shift is from a row\n
          shiftedRange.first[0]++;\n
          shiftedRange.last[0]++;\n
        }\n
        \n
        if (!isBefore \046\046 colOffset) { //this shift is from a col\n
          shiftedRange.first[1]++;\n
          shiftedRange.last[1]++;\n
        }\n
        \n
        function isInFormula(loc) {\n
          if ((loc[0] - 1) \076= shiftedRange.first[0] \046\046\n
            (loc[1] - 1) \076= shiftedRange.first[1] \046\046\n
            (loc[0] - 1) \074= shiftedRange.last[0] \046\046\n
            (loc[1] - 1) \074= shiftedRange.last[1]\n
          ) {\n
            return true;\n
          } else {\n
            return false;\n
          }\n
        }\n
        \n
        function isInFormulaRange(startLoc, endLoc) {\n
          if (\n
            (\n
              (startLoc[0] - 1) \076= shiftedRange.first[0] \046\046\n
              (startLoc[1] - 1) \076= shiftedRange.first[1]\n
            ) \046\046 (\n
              (startLoc[0] - 1) \074= shiftedRange.last[0] \046\046\n
              (startLoc[1] - 1) \074= shiftedRange.last[1]\n
            ) \046\046 (\n
              (endLoc[0] - 1) \076= shiftedRange.first[0] \046\046\n
              (endLoc[1] - 1) \076= shiftedRange.first[1]\n
            ) \046\046 (\n
              (endLoc[0] - 1) \074= shiftedRange.last[0] \046\046\n
              (endLoc[1] - 1) \074= shiftedRange.last[1]\n
            )\n
          ) {\n
            return true;\n
          } else {\n
            return false;\n
          }\n
        }\n
        \n
        function reparseFormula(loc) {\n
          return ( //A1\n
            cE.columnLabelString(loc[1] + colOffset) + (loc[0] + rowOffset)\n
          );\n
        }\n
        \n
        function reparseFormulaRange(startLoc, endLoc) {\n
          return ( //A1:B4\n
            (cE.columnLabelString(startLoc[1] + colOffset) + (startLoc[0] + rowOffset)) + \':\' + \n
            (cE.columnLabelString(endLoc[1] + colOffset) + (endLoc[0] + rowOffset))\n
          );\n
        }\n
        \n
        jS.cycleCells(function (td) {\n
          var formula = td.attr(\'formula\');\n
          \n
          if (formula \046\046 jS.isFormulaEditable(td)) {\n
            formula = formula.replace(cE.regEx.cell, \n
              function(ignored, colStr, rowStr, pos) {\n
                var charAt = [formula.charAt(pos - 1), formula.charAt(ignored.length + pos)]; //find what is exactly before and after formula\n
                if (!colStr.match(cE.regEx.sheet) \046\046\n
                  charAt[0] != \':\' \046\046\n
                  charAt[1] != \':\'\n
                ) { //verify it\'s not a range or an exact location\n
                  \n
                  var colI = cE.columnLabelIndex(colStr);\n
                  var rowI = parseInt(rowStr);\n
                  \n
                  if (isInFormula([rowI, colI])) {\n
                    return reparseFormula([rowI, colI]);\n
                  } else {\n
                    return ignored;\n
                  }\n
                } else {\n
                  return ignored;\n
                }\n
            });\n
            formula = formula.replace(cE.regEx.range, \n
              function(ignored, startColStr, startRowStr, endColStr, endRowStr, pos) {\n
                var charAt = [formula.charAt(pos - 1), formula.charAt(ignored.length + pos)]; //find what is exactly before and after formula\n
                if (!startColStr.match(cE.regEx.sheet) \046\046\n
                  charAt[0] != \':\'\n
                ) {\n
                  \n
                  var startRowI = parseInt(startRowStr);\n
                  var startColI = cE.columnLabelIndex(startColStr);\n
                  \n
                  var endRowI = parseInt(endRowStr);\n
                  var endColI = cE.columnLabelIndex(endColStr);\n
                  \n
                  if (isInFormulaRange([startRowI, startColI], [endRowI, endColI])) {\n
                    return reparseFormulaRange([startRowI, startColI], [endRowI, endColI]);\n
                  } else {\n
                    return ignored;\n
                  }\n
                } else {\n
                  return ignored;\n
                }\n
            });\n
            \n
            td.attr(\'formula\', formula);\n
          }\n
\n
        }, [0, 0], shiftedRange.last);\n
        \n
        jS.calc();\n
      },\n
      cycleCells: function(fn, firstLoc, lastLoc) { /* cylces through a certain group of cells in a spreadsheet and applies a function to them\n
                              fn: function, the function to apply to a cell;\n
                              firstLoc: array of int - [col, row], the group to start;\n
                              lastLoc: array of int - [col, row], the group to end;\n
                            */\n
        for (var i = firstLoc[0]; i \074 lastLoc[0]; i++) {\n
          for (var j = firstLoc[1]; j \074 lastLoc[1]; j++) {\n
            var td = jS.getTd(jS.i, i, j);\n
            if (td) {\n
              fn(jQuery(td));\n
            }\n
          }\n
        }\n
      },\n
      cycleCellsAndMaintainPoint: function(fn, firstLoc, lastLoc) { /* cylces through a certain group of cells in a spreadsheet and applies a function to them, firstLoc can be bigger then lastLoc, this is more dynamic\n
                                      fn: function, the function to apply to a cell;\n
                                      firstLoc: array of int - [col, row], the group to start;\n
                                      lastLoc: array of int - [col, row], the group to end;\n
                                    */\n
        var o = [];\n
        for (var i = (firstLoc[0] \074 lastLoc[0] ? firstLoc[0] : lastLoc[0]) ; i \074= (firstLoc[0] \076 lastLoc[0] ? firstLoc[0] : lastLoc[0]); i++) {\n
          for (var j = (firstLoc[1] \074 lastLoc[1] ? firstLoc[1] : lastLoc[1]); j \074= (firstLoc[1] \076 lastLoc[1] ? firstLoc[1] : lastLoc[[1]]); j++) {\n
            o.push(jS.getTd(jS.i, i, j));\n
            fn(o[o.length - 1]);\n
          }\n
        }\n
        return o;\n
      },\n
      offsetFormula: function(formula, rowOffset, colOffset) { /* makes cell formulas increment\n
                                      formula: string, a cell\'s formula;\n
                                      rowOffset: int, offsets row increment;\n
                                      colOffset: int, offsets col increment;\n
                                  */\n
        //Cell References Fixed\n
        var charAt = [];\n
        var col = \'\';\n
        var row = \'\';\n
        formula = formula.replace(cE.regEx.cell, \n
          function(ignored, colStr, rowStr, pos) {\n
            charAt[0] = formula.charAt(pos - 1);\n
            charAt[1] = formula.charAt(ignored.length + pos);\n
            \n
            charAt[0] = (charAt[0] ? charAt[0] : \'\');\n
            charAt[1] = (charAt[1] ? charAt[1] : \'\');\n
            \n
            if (colStr.match(cE.regEx.sheet) || \n
              charAt[0] == \':\' || \n
              charAt[1] == \':\'\n
            ) { //verify it\'s not a range or an exact location\n
              return ignored;\n
            } else {\n
              row = parseInt(rowStr) + rowOffset;\n
              col = cE.columnLabelIndex(colStr) + colOffset;\n
              row = (row \076 0 ? row : \'1\'); //table rows are never negative\n
              col = (col \076 0 ? col : \'1\'); //table cols are never negative\n
              \n
              return cE.columnLabelString(col) + row;\n
            }\n
          }\n
        );\n
        return formula;\n
      },\n
      addTab: function() { /* Adds a tab for navigation to a spreadsheet */\n
        jQuery(\'\074span class="\' + jS.cl.uiTab + \' ui-corner-bottom"\076\' + \n
            \'\074a class="\' + jS.cl.tab + \'" id="\' + jS.id.tab + jS.i + \'" i="\' + jS.i + \'"\076\' + jS.sheetTab(true) + \'\074/a\076\' + \n
          \'\074/span\076\')\n
            .insertBefore(\n
              jS.obj.tabContainer().find(\'span:last\')\n
            );\n
      },\n
      sheetDecorate: function(o) { /* preps a table for use as a sheet;\n
                      o: object, table object;\n
                    */\n
        jS.formatSheet(o);\n
        jS.sheetSyncSizeToCols(o);\n
        jS.sheetDecorateRemove();\n
      },\n
      formatSheet: function(o) { /* adds tbody, colgroup, heights and widths to different parts of a spreadsheet\n
                      o: object, table object;\n
                    */\n
        var tableWidth = 0;\n
        if (o.find(\'tbody\').length \074 1) {\n
          o.wrapInner(\'\074tbody /\076\');\n
        }\n
        \n
        if (o.find(\'colgroup\').length \074 1 || o.find(\'col\').length \074 1) {\n
          o.remove(\'colgroup\');\n
          var colgroup = jQuery(\'\074colgroup /\076\');\n
          o.find(\'tr:first\').find(\'td,th\').each(function() {\n
            var w = s.newColumnWidth;\n
            jQuery(\'\074col /\076\')\n
              .width(w)\n
              .css(\'width\', (w) + \'px\')\n
              .attr(\'width\', (w) + \'px\')\n
              .appendTo(colgroup);\n
            \n
            tableWidth += w;\n
          });\n
          o.find(\'tr\').each(function() {\n
            jQuery(this)\n
              .height(s.colMargin)\n
              .css(\'height\', s.colMargin + \'px\')\n
              .attr(\'height\', s.colMargin + \'px\');\n
          });\n
          colgroup.prependTo(o);\n
        }\n
        \n
        o\n
          .removeAttr(\'width\')\n
          .css(\'width\', \'\')\n
          .width(tableWidth);\n
      },\n
      checkMinSize: function(o) { /* ensure sheet minimums have been met, if not add columns and rows\n
                      o: object, table object;\n
                    */\n
        var loc = jS.sheetSize();\n
        \n
        var addRows = 0;\n
        var addCols = 0;\n
        \n
        if ((loc[1]) \074 s.minSize.cols) {\n
          addCols = s.minSize.cols - loc[1] - 1;\n
        }\n
        \n
        if (addCols) {\n
          jS.controlFactory.addColumnMulti(addCols, false, true);\n
        }\n
        \n
        if ((loc[0]) \074 s.minSize.rows) {\n
          addRows = s.minSize.rows - loc[0] - 1;\n
        }\n
        \n
        if (addRows) {\n
          jS.controlFactory.addRowMulti(addRows, false, true);\n
        }\n
      },\n
      themeRoller: { /* jQuery ui Themeroller integration */\n
        start: function() {\n
          //Style sheet     \n
          s.parent.addClass(jS.cl.uiParent);\n
          jS.obj.sheet().addClass(jS.cl.uiSheet);\n
          //Style bars\n
          jS.obj.barLeft().find(\'div\').addClass(jS.cl.uiBar);\n
          jS.obj.barTop().find(\'div\').addClass(jS.cl.uiBar);\n
          jS.obj.barCornerParent().addClass(jS.cl.uiBar);\n
          \n
          jS.obj.controls().addClass(jS.cl.uiControl);\n
          jS.obj.label().addClass(jS.cl.uiControl);\n
          jS.obj.formula().addClass(jS.cl.uiControlTextBox);\n
        },\n
        cell: {\n
          setActive: function() {\n
            this.clearActive();\n
            this.setHighlighted(\n
              jS.cellLast.td\n
                .addClass(jS.cl.cellActive)\n
            );\n
          },\n
          setHighlighted: function(td) {\n
            jQuery(td)\n
              .addClass(jS.cl.cellHighlighted + \' \' + jS.cl.uiCellHighlighted);\n
          },\n
          clearActive: function() {\n
            jS.obj.cellActive()\n
              .removeClass(jS.cl.cellActive);\n
          },\n
          clearHighlighted: function() {\n
            jS.obj.cellHighlighted()\n
              .removeClass(jS.cl.cellHighlighted + \' \' + jS.cl.uiCellHighlighted);\n
            \n
            jS.highlightedLast.rowStart = -1;\n
            jS.highlightedLast.colStart = -1;\n
            jS.highlightedLast.rowEnd = -1;\n
            jS.highlightedLast.colEnd = -1;\n
          }\n
        },\n
        bar: {\n
          style: function(o) {\n
            jQuery(o).addClass(jS.cl.uiBar);\n
          },\n
          setActive: function(direction, i) {\n
            //We don\'t clear here because we can have multi active bars\n
            switch(direction) {\n
              case \'top\': jS.obj.barTop().find(\'div\').eq(i).addClass(jS.cl.uiActive);\n
                break;\n
              case \'left\': jS.obj.barLeft().find(\'div\').eq(i).addClass(jS.cl.uiActive);\n
                break;\n
            }\n
          },\n
          clearActive: function() {\n
            jS.obj.barTop().add(jS.obj.barLeft()).find(\'div.\' + jS.cl.uiActive)\n
              .removeClass(jS.cl.uiActive);\n
          }\n
        },\n
        tab: {\n
          setActive: function(o) {\n
            this.clearActive();\n
            jS.obj.tab().parent().addClass(jS.cl.uiTabActive);\n
          },\n
          clearActive: function () {\n
            jS.obj.tabContainer().find(\'span.\' + jS.cl.uiTabActive)\n
              .removeClass(jS.cl.uiTabActive);\n
          }\n
        },\n
        resize: function() {// add resizable jquery.ui if available\n
          // resizable container div\n
          jS.resizable(s.parent, {\n
            minWidth: s.width * 0.5,\n
            minHeight: s.height * 0.5,\n
            start: function() {\n
              jS.obj.ui().hide();\n
            },\n
            stop: function() {\n
              jS.obj.ui().show();\n
              s.width = s.parent.width();\n
              s.height = s.parent.height();\n
              jS.sheetSyncSize();\n
            }\n
          });\n
          // resizable formula area - a bit hard to grab the handle but is there!\n
          var formulaResizeParent = jQuery(\'\074span /\076\');\n
          jS.resizable(jS.obj.formula().wrap(formulaResizeParent).parent(), {\n
            minHeight: jS.obj.formula().height(), \n
            maxHeight: 78,\n
            handles: \'s\',\n
            resize: function(e, ui) {\n
              jS.obj.formula().height(ui.size.height);\n
              jS.sheetSyncSize();\n
            }\n
          });\n
        }\n
      },\n
      resizable: function(o, settings) { /* jQuery ui resizeable integration\n
                          o: object, any object that neds resizing;\n
                          settings: object, the settings used with jQuery ui resizable;\n
                        */\n
        if (jQuery.ui \046\046 s.resizable) {\n
          if (o.attr(\'resizable\')) {\n
            o.resizable("destroy");\n
          }\n
          \n
          o\n
            .resizable(settings)\n
            .attr(\'resizable\', true);\n
        }\n
      },\n
      manageHtmlToText: function(v) { /* converts html to text for use in textareas\n
                        v: string, value to convert;\n
                      */\n
        v = jQuery.trim(v);\n
        if (v.charAt(0) != "=") {\n
          v = v.replace(/\046nbsp;/g, \' \')\n
            .replace(/\046gt;/g, \'\076\')\n
            .replace(/\046lt;/g, \'\074\')\n
            .replace(/\\t/g, \'\')\n
            .replace(/\\n/g, \'\')\n
            .replace(/\074br\076/g, \'\\r\')\n
            .replace(/\074BR\076/g, \'\\n\');\n
\n
          //jS.log("from html to text");\n
        }\n
        return v;\n
      },\n
      manageTextToHtml: function(v) { /* converts text to html for use in any object, probably a td/cell\n
                        v: string, value to convert;\n
                      */\n
        v = jQuery.trim(v);\n
        if (v.charAt(0) != "=") {\n
          v = v.replace(/\\t/g, \'\046nbsp;\046nbsp;\046nbsp;\046nbsp;\')\n
            .replace(/ /g, \'\046nbsp;\')\n
            .replace(/\076/g, \'\046gt;\')\n
            .replace(/\074/g, \'\046lt;\')\n
            .replace(/\\n/g, \'\074br\076\')\n
            .replace(/\\r/g, \'\074br\076\');\n
          \n
          //jS.log("from text to html");\n
        }\n
        return v;\n
      },\n
      sheetDecorateRemove: function(makeClone) { /* removes sheet decorations\n
                              makesClone: bool, creates a clone rather than the actual object;\n
                            */\n
        var o = (makeClone ? jS.obj.sheetAll().clone() : jS.obj.sheetAll());\n
        \n
        //Get rid of highlighted cells and active cells\n
        jQuery(o).find(\'td.\' + jS.cl.cellActive)\n
          .removeClass(jS.cl.cellActive + \' \' + jS.cl.uiCellActive);\n
          \n
        jQuery(o).find(\'td.\' + jS.cl.cellHighlighted)\n
          .removeClass(jS.cl.cellHighlighted + \' \' + jS.cl.uiCellHighlighted);\n
        /*\n
        //IE Bug, match width with css width\n
        jQuery(o).find(\'col\').each(function(i) {\n
          var v = jQuery(this).css(\'width\');\n
          v = ((v + \'\').match(\'px\') ? v : v + \'px\');\n
          jQuery(o).find(\'col\').eq(i).attr(\'width\', v);\n
        });\n
        */\n
        return o;\n
      },\n
      labelUpdate: function(v, setDirect) { /* updates the label so that the user knows where they are currently positioned\n
                          v: string or array of ints, new location value;\n
                          setDirect: bool, converts the array of a1 or [0,0] to "A1";\n
                        */\n
        if (!setDirect) {\n
          jS.obj.label().html(cE.columnLabelString(v[1] + 1) + (v[0] + 1));\n
        } else {\n
          jS.obj.label().html(v);\n
        }\n
      },\n
      cellEdit: function(td, isDrag) { /* starts cell to be edited\n
                        td: object, td object;\n
\n
                        isDrag: bool, should be determained by if the user is dragging their mouse around setting cells;\n
                        */\n
        jS.autoFillerNotGroup = true; //make autoFiller directional again.\n
        //This finished up the edit of the last cell\n
        jS.evt.cellEditDone();\n
        jS.followMe(td);\n
        var loc = jS.getTdLocation(td);\n
        \n
        //Show where we are to the user\n
        jS.labelUpdate(loc);\n
        \n
        var v = td.attr(\'formula\');\n
        if (!v) {\n
          v = jS.manageHtmlToText(td.html());\n
        }\n
        \n
        jS.obj.formula()\n
          .val(v)\n
          .focus()\n
          .select();\n
        jS.cellSetActive(td, loc, isDrag);\n
      },\n
      cellSetActive: function(td, loc, isDrag, directional, fnDone) { /* cell cell active to sheet, and highlights it for the user\n
                                        td: object, td object;\n
                                        loc: array of ints - [col, row];\n
                                        isDrag: bool, should be determained by if the user is dragging their mouse around setting cells;\n
                                        directional: bool, makes highlighting directional, only left/right or only up/down;\n
                                        fnDone: function, called after the cells are set active;\n
                                      */\n
        if (typeof(loc[1]) != \'undefined\') {\n
          jS.cellLast.td = td; //save the current cell/td\n
          \n
          jS.cellLast.row = jS.rowLast = loc[0];\n
          jS.cellLast.col = jS.colLast = loc[1];\n
          \n
          jS.themeRoller.bar.clearActive();\n
          jS.themeRoller.cell.clearHighlighted();\n
          \n
          jS.highlightedLast.td = td;\n
          \n
          jS.themeRoller.cell.setActive(); //themeroll the cell and bars\n
          jS.themeRoller.bar.setActive(\'left\', jS.cellLast.row);\n
          jS.themeRoller.bar.setActive(\'top\', jS.cellLast.col);\n
          \n
          var selectModel;\n
          var clearHighlightedModel;\n
          \n
          jS.highlightedLast.rowStart = loc[0];\n
          jS.highlightedLast.colStart = loc[1];\n
          jS.highlightedLast.rowLast = loc[0];\n
          jS.highlightedLast.colLast = loc[1];\n
          \n
          switch (s.cellSelectModel) {\n
            case \'excel\':\n
            case \'gdocs\':\n
              selectModel = function() {};\n
              clearHighlightedModel = jS.themeRoller.cell.clearHighlighted;\n
              break;\n
            case \'oo\':\n
              selectModel = function(target) {\n
                var td = jQuery(target);\n
                if (jS.isTd(td)) {\n
                  jS.cellEdit(td);\n
                }\n
              };\n
              clearHighlightedModel = function() {};\n
              break;\n
          }\n
          \n
          if (isDrag) {\n
            var lastLoc = loc; //we keep track of the most recent location because we don\'t want tons of recursion here\n
            jS.obj.pane()\n
              .mousemove(function(e) {\n
                var endLoc = jS.getTdLocation([e.target]);\n
                var ok = true;\n
                \n
                if (directional) {\n
                  ok = false;\n
                  if (loc[1] == endLoc[1] || loc[0] == endLoc[0]) {\n
                    ok = true;\n
                  }\n
                }\n
                \n
                if ((lastLoc[1] != endLoc[1] || lastLoc[0] != endLoc[0]) \046\046 ok) { //this prevents this method from firing too much\n
                  //clear highlighted cells if needed\n
                  clearHighlightedModel();\n
                  \n
                  //set current bars\n
                  jS.highlightedLast.colEnd = endLoc[1];\n
                  jS.highlightedLast.rowEnd = endLoc[0];\n
                  \n
                  //select active cell if needed\n
                  selectModel(e.target);\n
                  \n
                  //highlight the cells\n
                  jS.highlightedLast.td = jS.cycleCellsAndMaintainPoint(jS.themeRoller.cell.setHighlighted, loc, endLoc);\n
                }\n
                \n
                lastLoc = endLoc;\n
              });\n
            \n
            jQuery(document)\n
              .one(\'mouseup\', function() {\n
  \n
                jS.obj.pane()\n
                  .unbind(\'mousemove\')\n
                  .unbind(\'mouseup\');\n
                \n
                if (jQuery.isFunction(fnDone)) {\n
                  fnDone();\n
                }\n
              });\n
          }\n
        }\n
      },\n
      colLast: 0, /* the most recent used column */\n
      rowLast: 0, /* the most recent used row */\n
      cellLast: { /* the most recent used cell */\n
        td: jQuery(\'\074td /\076\'), //this is a dud td, so that we don\'t get errors\n
        row: -1,\n
        col: -1,\n
        isEdit: false\n
      }, /* the most recent highlighted cells */\n
      highlightedLast: {\n
        td: jQuery(\'\074td /\076\'),\n
        rowStart: -1,\n
        colStart: -1,\n
        rowEnd: -1,\n
        colEnd: -1\n
      },\n
      cellStyleToggle: function(setClass, removeClass) { /* sets a cells class for styling\n
                                  setClass: string, class(es) to set cells to;\n
                                  removeClass: string, class(es) to remove from cell if the setClass would conflict with;\n
                                */\n
        //Lets check to remove any style classes\n
        var uiCell = jS.obj.cellHighlighted();\n
        \n
        jS.cellUndoable.add(uiCell);\n
        \n
        if (removeClass) {\n
          uiCell.removeClass(removeClass);\n
        }\n
        //Now lets add some style\n
        if (uiCell.hasClass(setClass)) {\n
          uiCell.removeClass(setClass);\n
        } else {\n
          uiCell.addClass(setClass);\n
        }\n
        \n
        jS.cellUndoable.add(uiCell);\n
        \n
        jS.obj.formula()\n
          .focus()\n
          .select();\n
        return false;\n
      },\n
      fontReSize: function (direction) { /* resizes fonts in a cell by 1 pixel\n
                          direction: string, "up" || "down"\n
                        */\n
        var resize=0;\n
        switch (direction) {\n
          case \'up\':\n
            resize=1;\n
            break;\n
          case \'down\':\n
            resize=-1;\n
            break;    \n
        }\n
        \n
        //Lets check to remove any style classes\n
        var uiCell = jS.obj.cellHighlighted();\n
        \n
        jS.cellUndoable.add(uiCell);\n
        \n
        uiCell.each(function(i) {\n
          cell = jQuery(this);\n
          var curr_size = (cell.css("font-size") + \'\').replace("px","")\n
          var new_size = parseInt(curr_size ? curr_size : 10) + resize;\n
          cell.css("font-size", new_size + "px");\n
        });\n
        \n
        jS.cellUndoable.add(uiCell);\n
      },\n
      context: {},\n
      calc: function(tableI, fuel) { /* harnesses calculations engine\'s calculation function\n
                        tableI: int, the current table integer;\n
                        fuel: variable holder, used to prevent memory leaks, and for calculations;\n
                      */\n
        tableI = (tableI ? tableI : jS.i);\n
        jS.log(\'Calculation Started\');\n
        if (!jS.tableCellProviders[tableI]) {\n
          jS.tableCellProviders[tableI] = new jS.tableCellProvider(tableI);\n
        }\n
        if (!s.calcOff) {\n
          jS.tableCellProviders[tableI].cells = {};\n
          cE.calc(jS.tableCellProviders[tableI], jS.context, fuel);\n
          \n
          jQuery(document).trigger(\'calculation\');\n
          jS.isSheetEdit = false;\n
        }\n
        jS.log(\'Calculation Ended\');\n
      },\n
      refreshLabelsColumns: function(){ /* reset values inside bars for columns */\n
        var w = 0;\n
        jS.obj.barTop().find(\'div\').each(function(i) {\n
          jQuery(this).text(cE.columnLabelString(i+1));\n
          w += jQuery(this).width();\n
        });\n
        return w;\n
      },\n
      refreshLabelsRows: function(){ /* resets values inside bars for rows */\n
        jS.obj.barLeft().find(\'div\').each(function(i) {\n
          jQuery(this).text((i + 1));\n
        });\n
      },\n
      addSheet: function(size) { /* adds a spreadsheet\n
                      size: string example "10x100" which means 10 columns by 100 rows;\n
                    */\n
        size = (size ? size : prompt(jS.msg.newSheet));\n
        if (size) {\n
          jS.evt.cellEditAbandon();\n
          jS.setDirty(true);\n
          var newSheetControl = jS.controlFactory.sheetUI(jQuery.sheet.makeTable.fromSize(size), jS.sheetCount + 1, function(o) { \n
            jS.setActiveSheet(jS.sheetCount);\n
          }, true);\n
        }\n
      },\n
      deleteSheet: function() { /* removes the currently selected sheet */\n
        jS.obj.tableControl().remove();\n
        jS.obj.tabContainer().children().eq(jS.i).remove();\n
        jS.i = 0;\n
        jS.sheetCount--;\n
        \n
        jS.setControlIds();\n
        \n
        jS.setActiveSheet(jS.i);\n
      },\n
      deleteRow: function() { /* removes the currently selected row */\n
        var v = confirm(jS.msg.deleteRow);\n
        if (v) {\n
          jS.obj.barLeft().find(\'div\').eq(jS.rowLast).remove();\n
          jS.obj.sheet().find(\'tr\').eq(jS.rowLast).remove();\n
          \n
          jS.evt.cellEditAbandon();\n
          \n
          jS.setTdIds();\n
          jS.refreshLabelsRows();\n
          jS.obj.pane().scroll();\n
          \n
          jS.rowLast = -1;\n
          \n
          jS.offsetFormulaRange(jS.rowLast, 0, -1, 0);\n
        }   \n
      },\n
      deleteColumn: function() { /* removes the currently selected column */\n
        var v = confirm(jS.msg.deleteColumn);\n
        if (v) {\n
          jS.obj.barTop().find(\'div\').eq(jS.colLast).remove();\n
          jS.obj.sheet().find(\'colgroup col\').eq(jS.colLast).remove();\n
          jS.obj.sheet().find(\'tr\').each(function(i) {\n
              jQuery(this).find(\'td\').eq(jS.colLast).remove();\n
          });\n
          \n
          jS.evt.cellEditAbandon();\n
          \n
          var w = jS.refreshLabelsColumns();\n
          jS.setTdIds();\n
          jS.obj.sheet().width(w);\n
          jS.obj.pane().scroll();\n
          \n
          jS.colLast = -1;\n
          \n
          jS.offsetFormulaRange(0, jS.colLast, 0, -1);\n
        }   \n
      },\n
      sheetTab: function(get) { /* manages a tabs inner value\n
                      get: bool, makes return the current value of the tab;\n
                    */\n
        var sheetTab = \'\';\n
        if (get) {\n
          sheetTab = jS.obj.sheet().attr(\'title\');\n
          sheetTab = (sheetTab ? sheetTab : \'Spreadsheet \' + (jS.i + 1));\n
        } else if (s.editable) { //ensure that the sheet is editable, then let them change the sheet\'s name\n
          var newTitle = prompt("What would you like the sheet\'s title to be?", jS.sheetTab(true));\n
          if (!newTitle) { //The user didn\'t set the new tab name\n
            sheetTab = jS.obj.sheet().attr(\'title\');\n
            newTitle = (sheetTab ? sheetTab : \'Spreadsheet\' + (jS.i + 1));\n
          } else {\n
            jS.setDirty(true);\n
            jS.obj.sheet().attr(\'title\', newTitle);\n
            jS.obj.tab().html(newTitle);\n
            \n
            sheetTab = newTitle;\n
          }\n
        }\n
        return sheetTab;\n
      },\n
      print: function(o) { /* prints a value in a new window\n
                  o: string, any string;\n
                */\n
        var w = window.open();\n
        w.document.write("\074html\076\074body\076\074xmp\076" + o + "\\n\074/xmp\076\074/body\076\074/html\076");\n
        w.document.close();\n
      },\n
      getSource: function(pretty) {\n
        var sheetClone = jS.sheetDecorateRemove(true);\n
        var s = "";\n
        if (pretty) {\n
          jQuery(sheetClone).each(function() {\n
             s += jS.HTMLtoPrettySource(this);\n
          });\n
        } else {\n
          s += jQuery(\'\074div /\076\').html(sheetClone).html();\n
        }\n
          return s;\n
      },\n
      viewSource: function(pretty) { /* prints the source of a sheet for a user to see\n
                        pretty: bool, makes html a bit easier for the user to see;\n
                      */\n
        var sheetClone = jS.sheetDecorateRemove(true);\n
        \n
        var s = "";\n
        if (pretty) {\n
          jQuery(sheetClone).each(function() {\n
            s += jS.HTMLtoPrettySource(this);\n
          });\n
        } else {\n
          s += jQuery(\'\074div /\076\').html(sheetClone).html();\n
        }\n
        \n
        jS.print(s);\n
        \n
        return false;\n
      },\n
      saveSheet: function() { /* saves the sheet */\n
        var v = jS.sheetDecorateRemove(true);\n
        var d = jQuery(\'\074div /\076\').html(v).html();\n
\n
        jQuery.ajax({\n
          url: s.urlSave,\n
          type: \'POST\',\n
          data: \'s=\' + d,\n
          dataType: \'html\',\n
          success: function(data) {\n
            jS.setDirty(false);\n
            alert(\'Success! - \' + data);\n
          }\n
        });\n
      },\n
      HTMLtoCompactSource: function(node) { /* prints html to 1 line\n
                          node: object;\n
                        */\n
        var result = "";\n
        if (node.nodeType == 1) {\n
          // ELEMENT_NODE\n
          result += "\074" + node.tagName;\n
          hasClass = false;\n
          \n
          var n = node.attributes.length;\n
          for (var i = 0, hasClass = false; i \074 n; i++) {\n
            var key = node.attributes[i].name;\n
            var val = node.getAttribute(key);\n
            if (val) {\n
              if (key == "contentEditable" \046\046 val == "inherit") {\n
                continue;\n
                // IE hack.\n
              }\n
              if (key == "class") {\n
                hasClass = true;\n
              }\n
              \n
              if (typeof(val) == "string") {\n
                result += " " + key + \'="\' + val.replace(/"/g, "\'") + \'"\';\n
              } else if (key == "style" \046\046 val.cssText) {\n
                result += \' style="\' + val.cssText + \'"\';\n
              }\n
            }\n
          }\n
\n
          if (node.tagName == "COL") {\n
            // IE hack, which doesn\'t like \074COL..\076\074/COL\076.\n
            result += \'/\076\';\n
          } else {\n
            result += "\076";\n
            var childResult = "";\n
            jQuery(node.childNodes).each(function() {\n
              childResult += jS.HTMLtoCompactSource(this);\n
            });\n
            result += childResult;\n
            result += "\074/" + node.tagName + "\076";\n
          }\n
\n
        } else if (node.nodeType == 3) {\n
          // TEXT_NODE\n
          result += node.data.replace(/^\\s*(.*)\\s*$/g, "$1");\n
        }\n
        return result;\n
      },\n
      HTMLtoPrettySource: function(node, prefix) {/* prints html to manu lines, formatted for easy viewing\n
                              node: object;\n
                              prefix: string;\n
                            */\n
        if (!prefix) {\n
          prefix = "";\n
        }\n
        var result = "";\n
        if (node.nodeType == 1) {\n
          // ELEMENT_NODE\n
          result += "\\n" + prefix + "\074" + node.tagName;\n
          var n = node.attributes.length;\n
          for (var i = 0; i \074 n; i++) {\n
            var key = node.attributes[i].name;\n
            var val = node.getAttribute(key);\n
            if (val) {\n
              if (key == "contentEditable" \046\046 val == "inherit") {\n
                continue; // IE hack.\n
              }\n
              if (typeof(val) == "string") {\n
                result += " " + key + \'="\' + val.replace(/"/g, "\'") + \'"\';\n
              } else if (key == "style" \046\046 val.cssText) {\n
                result += \' style="\' + val.cssText + \'"\';\n
              }\n
            }\n
          }\n
          if (node.childNodes.length \074= 0) {\n
            result += "/\076";\n
          } else {\n
            result += "\076";\n
            var childResult = "";\n
            var n = node.childNodes.length;\n
            for (var i = 0; i \074 n; i++) {\n
              childResult += jS.HTMLtoPrettySource(node.childNodes[i], prefix + "  ");\n
            }\n
            result += childResult;\n
            if (childResult.indexOf(\'\\n\') \076= 0) {\n
              result += "\\n" + prefix;\n
            }\n
            result += "\074/" + node.tagName + "\076";\n
          }\n
        } else if (node.nodeType == 3) {\n
          // TEXT_NODE\n
          result += node.data.replace(/^\\s*(.*)\\s*$/g, "$1");\n
        }\n
        return result;\n
      },\n
      followMe: function(td) { /* scrolls the sheet to the selected cell\n
                    td: object, td object;\n
                  */\n
        td = (td ? td : jQuery(jS.cellLast.td));\n
        var pane = jS.obj.pane();\n
        var panePos = pane.offset();\n
        var paneWidth = pane.width();\n
        var paneHeight = pane.height();\n
\n
        var tdPos = td.offset();\n
        var tdWidth = td.width();\n
        var tdHeight = td.height();\n
        \n
        var margin = 20;\n
        \n
        //jS.log(\'td: [\' + tdPos.left + \', \' + tdPos.top + \']\');\n
        //jS.log(\'pane: [\' + panePos.left + \', \' + panePos.top + \']\');\n
        \n
        if ((tdPos.left + tdWidth + margin) \076 (panePos.left + paneWidth)) { //right\n
          pane.stop().scrollTo(td, {\n
            axis: \'x\',\n
            duration: 50,\n
            offset: - ((paneWidth - tdWidth) - margin)\n
          });\n
        } else if (tdPos.left \074 panePos.left) { //left\n
          pane.stop().scrollTo(td, {\n
            axis: \'x\',\n
            duration: 50\n
          });\n
        }\n
        \n
        if ((tdPos.top + tdHeight + margin) \076 (panePos.top + paneHeight)) { //bottom\n
          pane.stop().scrollTo(td, {\n
            axis: \'y\',\n
            duration: 50,\n
            offset: - ((paneHeight - tdHeight) - margin)\n
          });\n
        } else if (tdPos.top \074 panePos.top) { //top\n
          pane.stop().scrollTo(td, {\n
            axis: \'y\',\n
            duration: 50\n
          });\n
        }\n
        \n
        jS.autoFillerGoToTd(td, tdHeight, tdWidth);\n
      },\n
      autoFillerGoToTd: function(td, tdHeight, tdWidth) { /* moves autoFiller to a selected cell\n
                                  td: object, td object;\n
                                  tdHeight: height of a td object;\n
                                  tdWidth: width of a td object;\n
                                */\n
        td = (td ? td : jQuery(jS.cellLast.td));\n
        tdHeight = (tdHeight ? tdHeight : td.height());\n
        tdWidth = (tdWidth ? tdWidth : td.width());\n
        \n
        if (s.autoFiller) {\n
          if (td.attr(\'id\')) { //ensure that it is a usable cell\n
            tdPos = td.position();\n
            jS.obj.autoFiller()\n
              .show(\'slow\')\n
              .css(\'top\', ((tdPos.top + (tdHeight ? tdHeight : td.height()) - 3) + \'px\'))\n
              .css(\'left\', ((tdPos.left + (tdWidth ? tdWidth : td.width()) - 3) + \'px\'));\n
          }\n
        }\n
      },\n
      isRowHeightSync: [],\n
      setActiveSheet: function(i) { /* sets active a spreadsheet inside of a sheet instance \n
                      i: int, a sheet integer desired to show;\n
                      */\n
        i = (i ? i : 0);\n
\n
        jS.obj.tableControlAll().hide().eq(i).show();\n
        jS.i = i;     \n
        \n
        jS.themeRoller.tab.setActive();\n
        \n
        if (!jS.isRowHeightSync[i]) { //this makes it only run once, no need to have it run every time a user changes a sheet\n
          jS.isRowHeightSync[i] = true;\n
          jS.obj.sheet().find(\'tr\').each(function(j) {\n
            jS.attrH.setHeight(j, \'cell\');\n
            /*\n
            fixes a wired bug with height in chrome and ie\n
            It seems that at some point during the sheet\'s initializtion the height for each\n
            row isn\'t yet clearly defined, this ensures that the heights for barLeft match \n
            that of each row in the currently active sheet when a user uses a non strict doc type.\n
            */\n
          });\n
        }\n
        \n
        jS.sheetSyncSize();\n
        //jS.replaceWithSafeImg();\n
      },\n
      openSheetURL: function ( url ) { /* opens a table object from a url, then opens it\n
                        url: string, location;\n
                      */\n
        s.urlGet = url;\n
        return jS.openSheet();\n
      },\n
      openSheet: function(o, reloadBarsOverride) { /* opens a spreadsheet into the active sheet instance \\\n
                              o: object, a table object;\n
                              reloadBarsOverride: if set to true, foces bars on left and top not be reloaded;\n
                            */\n
        if (!jS.isDirty ? true : confirm(jS.msg.openSheet)) {\n
          jS.controlFactory.header();\n
          \n
          var fnAfter = function(i, l) {\n
            if (i == (l - 1)) {\n
              jS.i = 0;\n
              jS.setActiveSheet();\n
              jS.themeRoller.resize();\n
              for (var i = 0; i \074= jS.sheetCount; i++) {\n
                jS.calc(i);\n
              }\n
              \n
              s.fnAfter();\n
            }\n
          };\n
          \n
          if (!o) {\n
            jQuery(\'\074div /\076\').load(s.urlGet, function() {\n
              var sheets = jQuery(this).find(\'table\');\n
              sheets.each(function(i) {\n
                jS.controlFactory.sheetUI(jQuery(this), i, function() { \n
                  fnAfter(i, sheets.length);\n
                }, true);\n
              });\n
            });\n
          } else {\n
            var sheets = jQuery(\'\074div /\076\').html(o).children(\'table\');\n
            sheets.show().each(function(i) {\n
              jS.controlFactory.sheetUI(jQuery(this), i,  function() { \n
                fnAfter(i, sheets.length);\n
              }, (reloadBarsOverride ? true : false));\n
            });\n
          }\n
          \n
          jS.setDirty(false);\n
          \n
          return true;\n
        } else {\n
          return false;\n
        }\n
      },\n
      newSheet: function() { /* creates a new shet from size */\n
        var size = prompt(jS.msg.newSheet);\n
        if (size) {\n
          jS.openSheet(jQuery.sheet.makeTable.fromSize(size));\n
        }\n
      },\n
      importRow: function(rowArray) { /* creates a new row and then applies an array\'s values to each of it\'s new values\n
                        rowArray: array;\n
                      */\n
        jS.controlFactory.addRow(null, null, \':last\');\n
\n
        var error = "";\n
        jS.obj.sheet().find(\'tr:last td\').each(function(i) {\n
          jQuery(this).removeAttr(\'formula\');\n
          try {\n
            //To test this, we need to first make sure it\'s a string, so converting is done by adding an empty character.\n
            if ((rowArray[i] + \'\').charAt(0) == "=") {\n
              jQuery(this).attr(\'formula\', rowArray[i]);          \n
            } else {\n
              jQuery(this).html(rowArray[i]);\n
            }\n
          } catch(e) {\n
            //We want to make sure that is something bad happens, we let the user know\n
            error += e + \';\\n\';\n
          }\n
        });\n
        \n
        if (error) {//Show them the errors\n
          alert(error);\n
        }\n
        //Let\'s recalculate the sheet just in case\n
        jS.setTdIds();\n
        jS.calc();\n
      },\n
      importColumn: function(columnArray) { /* creates a new column and then applies an array\'s values to each of it\'s new values\n
                          columnArray: array;\n
                        */\n
        jS.controlFactory.addColumn();\n
\n
        var error = "";\n
        jS.obj.sheet().find(\'tr\').each(function(i) {\n
          var o = jQuery(this).find(\'td:last\');\n
          try {\n
            //To test this, we need to first make sure it\'s a string, so converting is done by adding an empty character.\n
            if ((columnArray[i] + \'\').charAt(0) == "=") {\n
              o.attr(\'formula\', columnArray[i]);          \n
            } else {\n
              o.html(columnArray[i]);\n
            }\n
          } catch(e) {\n
            //We want to make sure that is something bad happens, we let the user know\n
            error += e + \';\\n\';\n
          }\n
        });\n
        \n
        if (error) {//Show them the errors\n
          alert(error);\n
        }\n
        //Let\'s recalculate the sheet just in case\n
        jS.setTdIds();\n
        jS.calc();\n
      },\n
      exportSheet: { /* exports sheets into xml, json, or html formats */\n
        xml: function (skipCData) {\n
          var sheetClone = jS.sheetDecorateRemove(true);      \n
          var document = "";\n
          \n
          var cdata = [\'\074![CDATA[\',\']]\076\'];\n
          \n
          if (skipCData) {\n
            cdata = [\'\',\'\'];\n
          }\n
\n
          jQuery(sheetClone).each(function() {\n
            var row = \'\';\n
            var table = jQuery(this);\n
            var colCount = 0;\n
            var col_widths = \'\';\n
\n
            table.find(\'colgroup\').children().each(function (i) {\n
              col_widths += \'\074c\' + i + \'\076\' + (jQuery(this).attr(\'width\') + \'\').replace(\'px\', \'\') + \'\074/c\' + i + \'\076\';\n
            });\n
            \n
            var trs = table.find(\'tr\');\n
            var rowCount = trs.length;\n
            \n
            trs.each(function(i){\n
              var col = \'\';\n
              \n
              var tr = jQuery(this);\n
              var h = tr.attr(\'height\');\n
              var height = (h ? h : s.colMargin);\n
              var tds = tr.find(\'td\');\n
              colCount = tds.length;\n
              \n
              tds.each(function(j){\n
                var td = jQuery(this);\n
                var colSpan = td.attr(\'colspan\');\n
                colSpan = (colSpan \076 1 ? colSpan : \'\');\n
                \n
                var formula = td.attr(\'formula\');\n
                var text = (formula ? formula : td.text());\n
                var cl = td.attr(\'class\');\n
                var style = td.attr(\'style\');\n
                  \n
                //Add to current row\n
                col += \'\074c\' + j +\n
                  (style ? \' style=\\"\' + style + \'\\"\' : \'\') + \n
                  (cl ? \' class=\\"\' + cl + \'\\"\' : \'\') + \n
                  (colSpan ? \' colspan=\\"\' + colSpan + \'\\"\' : \'\') +\n
                \'\076\' + text + \'\074/c\' + j + \'\076\';\n
              });\n
              \n
              row += \'\074r\' + i + \' h=\\"\' + height + \'\\"\076\' + col + \'\074/r\' + i + \'\076\';\n
            });\n
\n
            document += \'\074document title="\' + table.attr(\'title\') + \'"\076\' +\n
                  \'\074metadata\076\' +\n
                    \'\074columns\076\' + colCount + \'\074/columns\076\' +  //length is 1 based, index is 0 based\n
                    \'\074rows\076\' + rowCount + \'\074/rows\076\' +  //length is 1 based, index is 0 based\n
                    \'\074col_widths\076\' + col_widths + \'\074/col_widths\076\' +\n
                  \'\074/metadata\076\' +\n
                  \'\074data\076\' + row + \'\074/data\076\' +\n
                \'\074/document\076\';\n
          });\n
\n
          return \'\074documents\076\' + document + \'\074/documents\076\';\n
        },\n
        json: function() {\n
          var sheetClone = jS.sheetDecorateRemove(true);\n
          var documents = []; //documents\n
          \n
          jQuery(sheetClone).each(function() {\n
            var document = {}; //document\n
            document[\'metadata\'] = {};\n
            document[\'data\'] = {};\n
            \n
            var table = jQuery(this);\n
            \n
            var trs = table.find(\'tr\');\n
            var rowCount = trs.length;\n
            var colCount = 0;\n
            var col_widths = \'\';\n
            \n
            trs.each(function(i) {\n
              var tr = jQuery(this);\n
              var tds = tr.find(\'td\');\n
              colCount = tds.length;\n
              \n
              document[\'data\'][\'r\' + i] = {};\n
              document[\'data\'][\'r\' + i][\'h\'] = tr.attr(\'height\');\n
              \n
              tds.each(function(j) {\n
                var td = jQuery(this);\n
                var colSpan = td.attr(\'colspan\');\n
                colSpan = (colSpan \076 1 ? colSpan : null);\n
                var formula = td.attr(\'formula\');\n
\n
                document[\'data\'][\'r\' + i][\'c\' + j] = {\n
                  \'value\': (formula ? formula : td.text()),\n
                  \'style\': td.attr(\'style\'),\n
                  \'colspan\': colSpan,\n
                  \'cl\': td.attr(\'class\')\n
                };\n
              });\n
            });\n
            document[\'metadata\'] = {\n
              \'columns\': colCount, //length is 1 based, index is 0 based\n
              \'rows\': rowCount, //length is 1 based, index is 0 based\n
              \'title\': table.attr(\'title\'),\n
              \'col_widths\': {}\n
            };\n
            \n
            table.find(\'colgroup\').children().each(function(i) {\n
              document[\'metadata\'][\'col_widths\'][\'c\' + i] = (jQuery(this).attr(\'width\') + \'\').replace(\'px\', \'\');\n
            });\n
            \n
            documents.push(document); //append to documents\n
          });\n
          return documents;\n
        },\n
        html: function() {\n
          return jS.sheetDecorateRemove(true);\n
        }\n
      },\n
      sheetSyncSizeToDivs: function() { /* syncs a sheet\'s size from bars/divs */\n
        var newSheetWidth = 0;\n
        jS.obj.barTop().find(\'div\').each(function() {\n
          newSheetWidth += parseInt(jQuery(this).outerWidth());\n
        });\n
        jS.obj.sheet().width(newSheetWidth);\n
      },\n
      sheetSyncSizeToCols: function(o) { /* syncs a sheet\'s size from it\'s col objects\n
                          o: object, sheet object;\n
                        */\n
        var newSheetWidth = 0;\n
        o = (o ? o : jS.obj.sheet());\n
        o.find(\'colgroup col\').each(function() {\n
          newSheetWidth += jQuery(this).width();\n
        });\n
        o.width(newSheetWidth);\n
      },\n
      sheetSyncSize: function() { /* syncs a sheet\'s size to that of the jQuery().sheet() caller object */\n
        var h = s.height;\n
        if (!h) {\n
          h = 400; //Height really needs to be set by the parent\n
        } else if (h \074 200) {\n
          h = 200;\n
        }\n
        s.parent\n
          .height(h)\n
          .width(s.width);\n
          \n
        var w = s.width - jS.attrH.width(jS.obj.barLeftParent()) - (s.boxModelCorrection);\n
        \n
        h = h - jS.attrH.height(jS.obj.controls()) - jS.attrH.height(jS.obj.barTopParent()) - (s.boxModelCorrection * 2);\n
        \n
        jS.obj.pane()\n
          .height(h)\n
          .width(w)\n
          .parent()\n
            .width(w);\n
        \n
        jS.obj.ui()\n
          .width(w + jS.attrH.width(jS.obj.barLeftParent()));\n
            \n
        jS.obj.barLeftParent()\n
          .height(h);\n
        \n
        jS.obj.barTopParent()\n
          .width(w)\n
          .parent()\n
            .width(w);\n
      },\n
      cellChangeStyle: function(style, value) { /* changes a cell\'s style and makes it undoable/redoable\n
                            style: string, css style name;\n
                            value: string, css setting;\n
                          */\n
        jS.cellUndoable.add(jS.obj.cellHighlighted()); //save state, make it undoable\n
        jS.obj.cellHighlighted().css(style, value);\n
        jS.cellUndoable.add(jS.obj.cellHighlighted()); //save state, make it redoable\n
\n
      },\n
      cellFind: function(v) { /* finds a cell in a sheet from a value\n
                    v: string, value in a cell to find;\n
                  */\n
        if(!v) {\n
          v = prompt("What are you looking for in this spreadsheet?");\n
        }\n
        if (v) {//We just do a simple uppercase/lowercase search.\n
          var o = jS.obj.sheet().find(\'td:contains("\' + v + \'")\');\n
          \n
          if (o.length \074 1) {\n
            o = jS.obj.sheet().find(\'td:contains("\' + v.toLowerCase() + \'")\');\n
          }\n
          \n
          if (o.length \074 1) {\n
            o = jS.obj.sheet().find(\'td:contains("\' + v.toUpperCase() + \'")\');\n
          }\n
          \n
          o = o.eq(0);\n
          if (o.length \076 0) {\n
            jS.cellEdit(o);\n
          } else {\n
            alert(jS.msg.cellFind);\n
          }\n
        }\n
      },\n
      cellSetActiveBar: function(type, start, end) { /* sets a bar active\n
                                type: string, "col" || "row" || "all";\n
                                start: int, int to start highlighting from;\n
                                start: int, int to end highlighting to;\n
                              */\n
        var loc = jS.sheetSize();\n
        var first = (start \074 end ? start : end);\n
        var last = (start \074 end ? end : start);\n
        \n
        var setActive = function(td, rowStart, colStart, rowFollow, colFollow) {\n
          switch (s.cellSelectModel) {\n
            case \'oo\': //follow cursor behavior\n
              jS.cellEdit(jQuery(jS.getTd(jS.i, rowFollow, colFollow)));\n
              break;\n
            default: //stay at initial cell\n
              jS.cellEdit(jQuery(jS.getTd(jS.i, rowStart, colStart)));\n
              break;\n
          }\n
          \n
          setActive = function(td) { //save resources\n
            return td;\n
          };\n
          \n
          return td;\n
        };\n
\n
        var cycleFn;\n
\n
        var td = [];\n
        \n
        switch (type) {\n
          case \'col\':\n
            cycleFn = function() {\n
              for (var i = 0; i \074= loc[0]; i++) { //rows\n
                for (var j = first; j \074= last; j++) { //cols\n
                  td.push(jS.getTd(jS.i, i, j));\n
                  jS.themeRoller.cell.setHighlighted(setActive(td[td.length - 1], 0, start, 0, end));\n
                }\n
              }\n
            };\n
            break;\n
          case \'row\':\n
            cycleFn = function() {\n
              for (var i = first; i \074= last; i++) { //rows\n
                for (var j = 0; j \074= loc[1]; j++) { //cols\n
                  td.push(jS.getTd(jS.i, i, j));\n
                  jS.themeRoller.cell.setHighlighted(setActive(td[td.length - 1], start, 0, end, 0));\n
                }\n
              }\n
            };\n
            break;\n
          case \'all\':\n
            cycleFn = function() {\n
              setActive = function(td) {\n
                jS.cellEdit(jQuery(td));\n
                setActive = function() {};\n
              };\n
              for (var i = 0; i \074= loc[0]; i++) {\n
                for (var j = 0; j \074= loc[1]; j++) {\n
                  td.push(jS.getTd(jS.i, i, j));\n
                  setActive(td[td.length - 1]);\n
                  jS.themeRoller.cell.setHighlighted(td[td.length - 1]);\n
                }\n
              }\n
              first = [0, 0];\n
              last = loc;\n
            };\n
            break;\n
        }\n
        \n
        cycleFn();\n
        \n
        jS.highlightedLast.td = td;\n
        jS.highlightedLast.rowStart = first[0];\n
        jS.highlightedLast.colStart = first[1];\n
        jS.highlightedLast.rowEnd = last[0];\n
        jS.highlightedLast.colEnd = last[1];\n
      },\n
      sheetClearActive: function() { /* clears formula and bars from being highlighted */\n
        jS.obj.formula().val(\'\');\n
        jS.obj.barSelected().removeClass(jS.cl.barSelected);\n
      },\n
      getTdRange: function(e, v, newFn, notSetFormula) { /* gets a range of selected cells, then returns it */\n
        jS.cellLast.isEdit = true;\n
        \n
        var range = function(loc) {\n
          if (loc.first[1] \076 loc.last[1] ||\n
            loc.first[0] \076 loc.last[0]\n
          ) {\n
            return {\n
              first: cE.columnLabelString(loc.last[1] + 1) + (loc.last[0] + 1),\n
              last: cE.columnLabelString(loc.first[1] + 1) + (loc.first[0] + 1)\n
            };\n
          } else {\n
            return {\n
              first: cE.columnLabelString(loc.first[1] + 1) + (loc.first[0] + 1),\n
              last: cE.columnLabelString(loc.last[1] + 1) + (loc.last[0] + 1)\n
            };\n
          }\n
        };\n
        var label = function(loc) {\n
          var rangeLabel = range(loc);\n
          var v2 = v + \'\';\n
          v2 = (v2.match(/=/) ? v2 : \'=\' + v2); //make sure we can use this value as a formula\n
          \n
          if (newFn || v2.charAt(v2.length - 1) != \'(\') { //if a function is being sent, make sure it can be called by wrapping it in ()\n
            v2 = v2 + (newFn ? newFn : \'\') + \'(\';\n
          }\n
          \n
          var formula;\n
          var lastChar = \'\';\n
          if (rangeLabel.first != rangeLabel.last) {\n
            formula = rangeLabel.first + \':\' + rangeLabel.last;\n
          } else {\n
            formula = rangeLabel.first;\n
          }\n
          \n
          if (v2.charAt(v2.length - 1) == \'(\') {\n
            lastChar = \')\';\n
          }\n
          \n
          return v2 + formula + lastChar;\n
        };\n
        var newVal = \'\';\n
        \n
        if (e) { //if from an event, we use mousemove method\n
          var loc = {\n
            first: jS.getTdLocation([e.target])\n
          };\n
          \n
          var sheet = jS.obj.sheet().mousemove(function(e) {\n
            loc.last = jS.getTdLocation([e.target]);\n
            \n
            newVal = label(loc);\n
            \n
            if (!notSetFormula) {\n
              jS.obj.formula().val(newVal);\n
              jS.obj.inPlaceEdit().val(newVal);\n
            }\n
          });\n
          \n
          jQuery(document).one(\'mouseup\', function() {\n
            sheet.unbind(\'mousemove\');\n
            return newVal;\n
          });\n
        } else {\n
          var cells = jS.obj.cellHighlighted().not(jS.obj.cellActive());\n
          \n
          if (cells.length) {\n
            var loc = { //tr/td column and row index\n
              first: jS.getTdLocation(cells.first()),\n
              last: jS.getTdLocation(cells.last())\n
            };\n
            \n
            newVal = label(loc);\n
            \n
            if (!notSetFormula) {\n
              jS.obj.formula().val(newVal);\n
              jS.obj.inPlaceEdit().val(newVal);\n
            }\n
            \n
            return newVal;\n
          } else {\n
            return \'\';\n
          }\n
        }\n
      },\n
      getTdId: function(tableI, row, col) { /* makes a td if from values given\n
                          tableI: int, table integer;\n
                          row: int, row integer;\n
                          col: int, col integer;\n
                        */\n
        return I + \'_table\' + tableI + \'_cell_c\' + col + \'_r\' + row;\n
      },\n
      getTd: function(tableI, row, col) { /* gets a td\n
                          tableI: int, table integer;\n
                          row: int, row integer;\n
                          col: int, col integer;\n
                        */\n
        return document.getElementById(jS.getTdId(tableI, row, col));\n
      },\n
      getTdLocation: function(td) { /* gets td column and row int\n
                        td: object, td object;\n
                      */\n
        var col = parseInt(td[0].cellIndex);\n
        var row = parseInt(td[0].parentNode.rowIndex);\n
        return [row, col];\n
        // The row and col are 1-based.\n
      },\n
      getTdFromXY: function(left, top, skipOffset) { /* gets cell from point\n
                                left: int, pixels left;\n
                                top: int, pixels top;\n
                                skipOffset: bool, skips pane offset;\n
                              */\n
        var pane = jS.obj.pane();\n
        var paneOffset = (skipOffset ? {left: 0, top: 0} : pane.offset());\n
        \n
        top += paneOffset.top + 2;\n
        left += paneOffset.left + 2;\n
        \n
        //here we double check that the coordinates are inside that of the pane, if so then we can continue\n
        if ((top \076= paneOffset.top \046\046 top \074= paneOffset.top + pane.height()) \046\046\n
          (left \076= paneOffset.left \046\046 left \074= paneOffset.left + pane.width())) {\n
          var td = jQuery(document.elementFromPoint(left - $window.scrollLeft(), top - $window.scrollTop()));\n
          \n
          \n
          //I use this snippet to help me know where the point was positioned\n
          /*jQuery(\'\074div class="ui-widget-content" style="position: absolute;"\076TESTING TESTING\074/div\076\')\n
            .css(\'top\', top + \'px\')\n
            .css(\'left\', left + \'px\')\n
            .appendTo(\'body\');\n
          */\n
          \n
          if (jS.isTd(td)) {\n
            return td;\n
          }\n
          return false;\n
        }\n
      },\n
      getBarLeftIndex: function(o) { /* get\'s index from object */\n
        var i = jQuery.trim(jQuery(o).text());\n
        return parseInt(i) - 1;\n
      },\n
      getBarTopIndex: function(o) { /* get\'s index from object */\n
        var i = cE.columnLabelIndex(jQuery.trim(jQuery(o).text()));\n
        return parseInt(i) - 1;\n
      },\n
      tableCellProvider: function(tableI) { /* provider for calculations engine */\n
        this.tableBodyId = jS.id.sheet + tableI;\n
        this.tableI = tableI;\n
        this.cells = {};\n
      },\n
      tableCellProviders: [],\n
      tableCell: function(tableI, row, col) { /* provider for calculations engine */\n
        this.tableBodyId = jS.id.sheet + tableI;\n
        this.tableI = tableI;\n
        this.row = row;\n
        this.col = col;\n
        this.value = jS.EMPTY_VALUE;\n
        \n
        //this.prototype = new cE.cell();\n
      },\n
      EMPTY_VALUE: {},\n
      time: { /* time loggin used with jS.log, useful for finding out if new methods are faster */\n
        now: new Date(),\n
        last: new Date(),\n
        diff: function() {\n
          return Math.abs(Math.ceil(this.last.getTime() - this.now.getTime()) / 1000).toFixed(5);\n
        },\n
        set: function() {\n
          this.last = this.now;\n
          this.now = new Date();\n
        },\n
        get: function() {\n
          return this.now.getHours() + \':\' + this.now.getMinutes() + \':\' + this.now.getSeconds();\n
        }\n
      },\n
      log: function(msg) {  //The log prints: {Current Time}, {Seconds from last log};{msg}\n
        jS.time.set();\n
        jS.obj.log().prepend(jS.time.get() + \', \' + jS.time.diff() + \'; \' + msg + \'\074br /\076\\n\');\n
      },\n
      replaceWithSafeImg: function(o) {  //ensures all pictures will load and keep their respective bar the same size.\n
        (o ? o : jS.obj.sheet().find(\'img\')).each(function() {      \n
          var src = jQuery(this).attr(\'src\');\n
          jQuery(this).replaceWith(jS.controlFactory.safeImg(src, jS.getTdLocation(jQuery(this).parent())[0]));\n
        });\n
      },\n
      \n
      isDirty:  false,\n
      setDirty: function(dirty) { jS.isDirty = dirty; },\n
      appendToFormula: function(v, o) {\n
        var formula = jS.obj.formula();\n
        \n
        var fV = formula.val();\n
        \n
        if (fV.charAt(0) != \'=\') {\n
          fV = \'=\' + fV;\n
        }\n
        \n
        formula.val(fV + v);\n
      },\n
      cellUndoable: { /* makes cell editing undoable and redoable */\n
        undoOrRedo: function(undo) {\n
          //hide the autoFiller, it can get confused\n
          if (s.autoFiller) {\n
            jS.obj.autoFiller().hide();\n
          }\n
          \n
          if (!undo \046\046 this.i \076 0) {\n
            this.i--;\n
          } else if (undo \046\046 this.i \074 this.stack.length) {\n
            this.i++;\n
          }\n
          \n
          this.get().clone().each(function() {\n
            var o = jQuery(this);\n
            var id = o.attr(\'undoable\');\n
            if (id) {\n
              jQuery(\'#\' + id).replaceWith(\n
                o\n
                  .removeAttr(\'undoable\')\n
                  .attr(\'id\', id)\n
              );\n
            } else {\n
              jS.log(\'Not available.\');\n
            }\n
          });\n
          \n
          jS.themeRoller.cell.clearActive();\n
          jS.themeRoller.bar.clearActive();\n
          jS.themeRoller.cell.clearHighlighted();\n
        },\n
        get: function() { //gets the current cell\n
          return jQuery(this.stack[this.i]);\n
        },\n
        add: function(tds) {\n
          var oldTds = tds.clone().each(function() {\n
            var o = jQuery(this);\n
            var id = o.attr(\'id\');\n
            o\n
              .removeAttr(\'id\') //id can only exist in one location, on the sheet, so here we use the id as the attr \'undoable\'\n
              .attr(\'undoable\', id)\n
              .removeClass(jS.cl.cellHighlighted + \' \' + jS.cl.uiCellHighlighted);\n
          });\n
          if (this.stack.length \076 0) {\n
            this.stack.unshift(oldTds);\n
          } else {\n
            this.stack = [oldTds];\n
          }\n
          this.i = -1;\n
          if (this.stack.length \076 20) { //undoable count, we want to be careful of too much memory consumption\n
            this.stack.pop(); //drop the last value\n
          }\n
        },\n
        i: 0,\n
        stack: []\n
      },\n
      sheetSize: function() {\n
        return jS.getTdLocation(jS.obj.sheet().find(\'td:last\'));\n
      },\n
      toggleState:  function(replacementSheets) {\n
        if (s.allowToggleState) {\n
          if (s.editable) {\n
            jS.evt.cellEditAbandon();\n
            jS.saveSheet();\n
          }\n
          jS.setDirty(false);\n
          s.editable = !s.editable;\n
          jS.obj.tabContainer().remove();\n
          var sheets = (replacementSheets ? replacementSheets : jS.obj.sheetAll().clone());\n
          origParent.children().remove();\n
          jS.openSheet(sheets, true);\n
        }\n
      },\n
      setCellRef: function(ref) {\n
        var td = jS.obj.cellActive();\n
        var cellRef = td.attr(\'cellRef\');\n
        td.removeClass(cellRef);\n
        \n
        cellRef = (ref ? ref : prompt(\'Enter the name you would like to reference the cell by.\'));\n
        \n
        if (cellRef) {\n
          td\n
            .addClass(cellRef)\n
            .attr(\'cellRef\', cellRef);\n
        }\n
        \n
        jS.calc();\n
      }\n
    };\n
\n
    jS.tableCellProvider.prototype = {\n
      getCell: function(tableI, row, col) {\n
        if (typeof(col) == "string") {\n
          col = cE.columnLabelIndex(col);\n
        }\n
        var key = tableI + "," + row + "," + col;\n
        var cell = this.cells[key];\n
        if (!cell) {\n
          var td = jS.getTd(tableI, row - 1, col - 1);\n
          if (td) {\n
            cell = this.cells[key] = new jS.tableCell(tableI, row, col);\n
          }\n
        }\n
        return cell;\n
      },\n
      getNumberOfColumns: function(row) {\n
        var tableBody = document.getElementById(this.tableBodyId);\n
        if (tableBody) {\n
          var tr = tableBody.rows[row];\n
          if (tr) {\n
            return tr.cells.length;\n
          }\n
        }\n
        return 0;\n
      },\n
      toString: function() {\n
        result = "";\n
        jQuery(\'#\' + (this.tableBodyId) + \' tr\').each(function() {\n
          result += this.innerHTML.replace(/\\n/g, "") + "\\n";\n
        });\n
        return result;\n
      }\n
    };\n
\n
    jS.tableCell.prototype = {\n
      td: null,\n
      getTd: function() {\n
        if (!this.td) { //this attempts to check if the td is cached, then cache it if not, then return it\n
          this.td = document.getElementById(jS.getTdId(this.tableI, this.row - 1, this.col - 1)); \n
        }\n
        \n
        return this.td;\n
      },\n
      setValue: function(v, e) {\n
        this.error = e;\n
        this.value = v;\n
        jQuery(this.getTd()).html(v ? v: \'\'); //I know this is slower than innerHTML = \'\', but sometimes stability just rules!\n
      },\n
      getValue: function() {\n
        var v = this.value;\n
        if (v === jS.EMPTY_VALUE \046\046 !this.getFormula()) {\n
          \n
          v = jQuery(this.getTd()).text(); //again, stability rules!\n
\n
          v = this.value = (v.length \076 0 ? cE.parseFormulaStatic(v) : null);\n
        }\n
        \n
        return (v === jS.EMPTY_VALUE ? null: v);\n
      },\n
      getFormat: function() {\n
        return jQuery(this.getTd()).attr("format");\n
      },\n
      setFormat: function(v) {\n
        jQuery(this.getTd()).attr("format", v);\n
      },\n
      getFormulaFunc: function() {\n
        return this.formulaFunc;\n
      },\n
      setFormulaFunc: function(v) {\n
        this.formulaFunc = v;\n
      },\n
      formula: null,\n
      getFormula: function() {\n
        if (!this.formula) { //this if statement takes line breaks out of formulas so that they calculate better, then they are cached because the formulas to not change, on the cell \n
          var v = jQuery(this.getTd()).attr(\'formula\'); \n
          this.formula = (v ? v.replace(/\\n/g, \' \') : v);\n
        }\n
        \n
        return this.formula;\n
      },\n
      setFormula: function(v) {\n
        if (v \046\046 v.length \076 0) {\n
          jQuery(this.getTd()).attr(\'formula\', v);\n
        } else {\n
          jQuery(this.getTd()).removeAttr(\'formula\');\n
        }\n
      }\n
    };\n
\n
    var cE = { //Calculations Engine\n
      TEST: {},\n
      ERROR: "#VALUE!",\n
      cFN: {//cFN = compiler functions, usually mathmatical\n
        sum:  function(x, y) { return x + y; },\n
        max:  function(x, y) { return x \076 y ? x: y; },\n
        min:  function(x, y) { return x \074 y ? x: y; },\n
        count:  function(x, y) { return (y != null) ? x + 1: x; },\n
        clean: function(v) {\n
          if (typeof(v) == \'string\') {\n
            v = v.replace(cE.regEx.amp, \'\046\')\n
                .replace(cE.regEx.nbsp, \' \')\n
                .replace(/\\n/g,\'\')\n
                .replace(/\\r/g,\'\');\n
          }\n
          return v;\n
        }\n
      },\n
      fn: {//fn = standard functions used in cells\n
        HTML: function(v) {\n
          return jQuery(v);\n
        },\n
        IMG: function(v) {\n
          return jS.controlFactory.safeImg(v, cE.calcState.row, cE.calcState.col);\n
        },\n
        AVERAGE:  function(values) { \n
          var arr =arrHelpers.foldPrepare(values, arguments);\n
          return cE.fn.SUM(arr) / cE.fn.COUNT(arr); \n
        },\n
        AVG:    function(values) { \n
          return cE.fn.AVERAGE(values);\n
        },\n
        COUNT:    function(values) { return arrHelpers.fold(arrHelpers.foldPrepare(values, arguments), cE.cFN.count, 0); },\n
        COUNTA:   function(v) {\n
          var values =arrHelpers.foldPrepare(v, arguments);\n
          var count = 0;\n
          for (var i = 0; i \074 values.length; i++) {\n
            if (values[i]) {\n
              count++;\n
            }\n
          }\n
          return count;\n
        },\n
        SUM:    function(values) { return arrHelpers.fold(arrHelpers.foldPrepare(values, arguments), cE.cFN.sum, 0, true, cE.fn.N); },\n
        MAX:    function(values) { return arrHelpers.fold(arrHelpers.foldPrepare(values, arguments), cE.cFN.max, Number.MIN_VALUE, true, cE.fn.N); },\n
        MIN:    function(values) { return arrHelpers.fold(arrHelpers.foldPrepare(values, arguments), cE.cFN.min, Number.MAX_VALUE, true, cE.fn.N); },\n
        MEAN:   function(values) { return this.SUM(values) / values.length; },\n
        ABS :     function(v) { return Math.abs(cE.fn.N(v)); },\n
        CEILING:  function(v) { return Math.ceil(cE.fn.N(v)); },\n
        FLOOR:    function(v) { return Math.floor(cE.fn.N(v)); },\n
        INT:    function(v) { return Math.floor(cE.fn.N(v)); },\n
        ROUND:    function(v, decimals) {\n
          return cE.fn.FIXED(v, (decimals ? decimals : 0), false);\n
        },\n
        RAND:     function(v) { return Math.random(); },\n
        RND:    function(v) { return Math.random(); },\n
        TRUE:     function() { return \'TRUE\'; },\n
        FALSE:    function() { return \'FALSE\'; },\n
        NOW:    function() { return new Date ( ); },\n
        TODAY:    function() { return Date( Math.floor( new Date ( ) ) ); },\n
        DAYSFROM:   function(year, month, day) { \n
          return Math.floor( (new Date() - new Date (year, (month - 1), day)) / 86400000);\n
        },\n
        DAYS: function(v1, v2) {\n
          var date1 = new Date(v1);\n
          var date2 = new Date(v2);\n
          var ONE_DAY = 1000 * 60 * 60 * 24;\n
          return Math.round(Math.abs(date1.getTime() - date2.getTime()) / ONE_DAY);\n
        },\n
        DATEVALUE: function(v) {\n
          var d = new Date(v);\n
          return d.getDate() + \'/\' + (d.getMonth() + 1) + \'/\' + d.getFullYear();\n
        },\n
        IF:     function(v, t, f){\n
          t = cE.cFN.clean(t);\n
          f = cE.cFN.clean(f);\n
          \n
          try { v = eval(v); } catch(e) {};\n
          try { t = eval(t); } catch(e) {};\n
          try { t = eval(t); } catch(e) {};\n
\n
          if (v == \'true\' || v == true || v \076 0 || v == \'TRUE\') {\n
            return t;\n
          } else {\n
            return f;\n
          }\n
        },\n
        FIXED:    function(v, decimals, noCommas) { \n
          if (decimals == null) {\n
            decimals = 2;\n
          }\n
          var x = Math.pow(10, decimals);\n
          var n = String(Math.round(cE.fn.N(v) * x) / x); \n
          var p = n.indexOf(\'.\');\n
          if (p \074 0) {\n
            p = n.length;\n
            n += \'.\';\n
          }\n
          for (var i = n.length - p - 1; i \074 decimals; i++) {\n
            n += \'0\';\n
          }\n
          if (noCommas == true) {// Treats null as false.\n
            return n;\n
          }\n
          var arr = n.replace(\'-\', \'\').split(\'.\');\n
          var result = [];\n
          var first  = true;\n
          while (arr[0].length \076 0) { // LHS of decimal point.\n
            if (!first) {\n
              result.unshift(\',\');\n
            }\n
            result.unshift(arr[0].slice(-3));\n
            arr[0] = arr[0].slice(0, -3);\n
            first = false;\n
          }\n
          if (decimals \076 0) {\n
            result.push(\'.\');\n
            var first = true;\n
            while (arr[1].length \076 0) { // RHS of decimal point.\n
              if (!first) {\n
                result.push(\',\');\n
              }\n
              result.push(arr[1].slice(0, 3));\n
              arr[1] = arr[1].slice(3);\n
              first = false;\n
            }\n
          }\n
          if (v \074 0) {\n
            return \'-\' + result.join(\'\');\n
          }\n
          return result.join(\'\');\n
        },\n
        TRIM:   function(v) { \n
          if (typeof(v) == \'string\') {\n
            v = jQuery.trim(v);\n
          }\n
          return v;\n
        },\n
        HYPERLINK: function(link, name) {\n
          name = (name ? name : \'LINK\');\n
          return jQuery(\'\074a href="\' + link + \'" target="_new" class="clickable"\076\' + name + \'\074/a\076\');\n
        },\n
        DOLLAR:   function(v, decimals, symbol) { \n
          if (decimals == null) {\n
            decimals = 2;\n
          }\n
          \n
          if (symbol == null) {\n
            symbol = \'$\';\n
          }\n
          \n
          var r = cE.fn.FIXED(v, decimals, false);\n
          \n
          if (v \076= 0) {\n
            return symbol + r; \n
          } else {\n
            return \'-\' + symbol + r.slice(1);\n
          }\n
        },\n
        VALUE:    function(v) { return parseFloat(v); },\n
        N:      function(v) { if (v == null) {return 0;}\n
                  if (v instanceof Date) {return v.getTime();}\n
                  if (typeof(v) == \'object\') {v = v.toString();}\n
                  if (typeof(v) == \'string\') {v = parseFloat(v.replace(cE.regEx.n, \'\'));}\n
                  if (isNaN(v))      {return 0;}\n
                  if (typeof(v) == \'number\') {return v;}\n
                  if (v == true)       {return 1;}\n
                  return 0; },\n
        PI:     function() { return Math.PI; },\n
        POWER:    function(x, y) {\n
          return Math.pow(x, y);\n
        },\n
        SQRT: function(v) {\n
          return Math.sqrt(v);\n
        },\n
        //Note, form objects are experimental, they don\'t work always as expected\n
        INPUT: {\n
          SELECT: function(v, noBlank) {\n
            if (s.editable) {\n
              v = arrHelpers.foldPrepare(v, arguments, true);\n
              return jS.controlFactory.input.select(v, noBlank);\n
            } else {\n
              return jS.controlFactory.input.getValue(v);\n
            }\n
          },\n
          RADIO: function(v) {\n
            if (s.editable) {\n
              v = arrHelpers.foldPrepare(v, arguments, true);\n
              return jS.controlFactory.input.radio(v);\n
            } else {\n
              return jS.controlFactory.input.getValue(v);\n
            }\n
          },\n
          CHECKBOX: function(v) {\n
            if (s.editable) {\n
              v = arrHelpers.foldPrepare(v, arguments)[0];\n
              return jS.controlFactory.input.checkbox(v);\n
            } else {\n
              return jS.controlFactory.input.getValue(v);\n
            }\n
          },\n
          VAL: function(v) {\n
            return jS.controlFactory.input.getValue(v);\n
          },\n
          SELECTVAL:  function(v) {\n
            return jS.controlFactory.input.getValue(v);\n
          },\n
          RADIOVAL: function(v) {\n
            return jS.controlFactory.input.getValue(v);\n
          },\n
          CHECKBOXVAL: function(v) {\n
            return jS.controlFactory.input.getValue(v);\n
          },\n
          ISCHECKED:    function(v) {\n
            var val = jS.controlFactory.input.getValue(v);\n
            var length = jQuery(v).find(\'input[value="\' + val + \'"]\').length;\n
            if (length) {\n
              return \'TRUE\';\n
            } else {\n
              return \'FALSE\';\n
            }\n
          }\n
        },\n
        CHART: {\n
          BAR:  function(values, legend, title) {\n
            return jS.controlFactory.chart({\n
              type: \'bar\',\n
              data: values,\n
              legend: legend,\n
              title: title\n
            });\n
          },\n
          HBAR: function(values, legend, title) {\n
            return jS.controlFactory.chart({\n
              type: \'hbar\',\n
              data: values,\n
              legend: legend,\n
              title: title\n
            });\n
          },\n
          LINE: function(valuesX, valuesY, legendX, legendY, title) {\n
            return jS.controlFactory.chart({\n
              type: \'line\',\n
              x: {\n
                data: valuesX,\n
                legend: legendX\n
              },\n
              y: {\n
                data: valuesY,\n
                legend: legendY\n
              },\n
              title: title\n
            });\n
          },\n
          PIE:  function(values, legend, title) {\n
            return jS.controlFactory.chart({\n
              type: \'pie\',\n
              data: values,\n
              legend: legend,\n
              title: title\n
            });\n
          },\n
          DOT:  function(valuesX, valuesY, values,legendX, legendY, title) {\n
            return jS.controlFactory.chart({\n
              type: \'dot\',\n
              values: values,\n
              x: {\n
                data: valuesX,\n
                legend: legendX\n
              },\n
              y: {\n
                data: valuesY,\n
                legend: legendY\n
              },\n
              title: title\n
            });\n
          }\n
        },\n
        CELLREF: function(v, i) {\n
          var td;\n
          if (i) {\n
            td = jS.obj.sheetAll().eq(i).find(\'td.\' + v);\n
          } else {\n
            td = jS.obj.sheet().find(\'td.\' + v);\n
          }\n
          \n
          return td.html();\n
        }\n
      },\n
      calcState: {},\n
      calc: function(cellProvider, context, startFuel) {\n
        // Returns null if all done with a complete calc() run.\n
        // Else, returns a non-null continuation function if we ran out of fuel.  \n
        // The continuation function can then be later invoked with more fuel value.\n
        // The fuelStart is either null (which forces a complete calc() to the finish) \n
        // or is an integer \076 0 to slice up long calc() runs.  A fuelStart number\n
        // is roughly matches the number of cells to visit per calc() run.\n
        cE.calcState = { \n
          cellProvider: cellProvider, \n
          context:    (context != null ? context : {}),\n
          row:      1, \n
          col:      1,\n
          i:        cellProvider.tableI,\n
          done:     false,\n
          stack:      [],\n
          calcMore:     function(moreFuel) {\n
                    cE.calcState.fuel = moreFuel;\n
                    return cE.calcLoop();\n
                  }\n
        };\n
        return cE.calcState.calcMore(startFuel);\n
      },\n
      calcLoop: function() {\n
        if (cE.calcState.done == true) {\n
          return null;\n
        } else {\n
          while (cE.calcState.fuel == null || cE.calcState.fuel \076 0) {\n
            if (cE.calcState.stack.length \076 0) {\n
              var workFunc = cE.calcState.stack.pop();\n
              if (workFunc != null) {\n
                workFunc(cE.calcState);\n
              }\n
            } else if (cE.calcState.cellProvider.formulaCells != null) {\n
              if (cE.calcState.cellProvider.formulaCells.length \076 0) {\n
                var loc = cE.calcState.cellProvider.formulaCells.shift();\n
                cE.visitCell(cE.calcState.i, loc[0], loc[1]);\n
              } else {\n
                cE.calcState.done = true;\n
                return null;\n
              }\n
            } else {\n
              if (cE.visitCell(cE.calcState.i, cE.calcState.row, cE.calcState.col) == true) {\n
                cE.calcState.done = true;\n
                return null;\n
              }\n
\n
              if (cE.calcState.col \076= cE.calcState.cellProvider.getNumberOfColumns(cE.calcState.row - 1)) {\n
                cE.calcState.row++;\n
                cE.calcState.col =  1;\n
              } else {\n
                cE.calcState.col++; // Sweep through columns first.\n
              }\n
            }\n
            \n
            if (cE.calcState.fuel != null) {\n
              cE.calcState.fuel -= 1;\n
            }\n
          }\n
          return cE.calcState.calcMore;\n
        }\n
      },\n
      visitCell: function(tableI, r, c) { // Returns true if done with all cells.\n
        var cell = cE.calcState.cellProvider.getCell(tableI, r, c);\n
        if (cell == null) {\n
          return true;\n
        } else {\n
          var value = cell.getValue();\n
          if (value == null) {\n
            this.formula = cell.getFormula();\n
            if (this.formula) {\n
              if (this.formula.charAt(0) == \'=\') {\n
                this.formulaFunc = cell.getFormulaFunc();\n
                if (this.formulaFunc == null ||\n
                  this.formulaFunc.formula != this.formula) {\n
                  this.formulaFunc = null;\n
                  try {\n
                    var dependencies = {};\n
                    var body = cE.parseFormula(this.formula.substring(1), dependencies, tableI);\n
                    this.formulaFunc = function() {\n
                      if (!body.match(/function/gi)) {\n
                        with (cE.fn) {\n
                          return eval(body);\n
                        }\n
                      } else {\n
                        return jS.msg.evalError;\n
                      }\n
                    };\n
                    \n
                    this.formulaFunc.formula = this.formula;\n
                    this.formulaFunc.dependencies = dependencies;\n
                    cell.setFormulaFunc(this.formulaFunc);\n
                  } catch (e) {\n
                    cell.setValue(cE.ERROR + \': \' + e);\n
                  }\n
                }\n
                if (this.formulaFunc) {\n
                  cE.calcState.stack.push(cE.makeFormulaEval(cell, r, c, this.formulaFunc));\n
\n
                  // Push the cell\'s dependencies, first checking for any cycles. \n
                  var dependencies = this.formulaFunc.dependencies;\n
                  for (var k in dependencies) {\n
                    if (dependencies[k] instanceof Array \046\046\n
                      (cE.checkCycles(dependencies[k][0], dependencies[k][1], dependencies[k][2]) == true) //same cell on same sheet\n
                    ) {\n
                      cell.setValue(cE.ERROR + \': cycle detected\');\n
                      cE.calcState.stack.pop();\n
                      return false;\n
                    }\n
                  }\n
                  for (var k in dependencies) {\n
                    if (dependencies[k] instanceof Array) {\n
                      cE.calcState.stack.push(cE.makeCellVisit(dependencies[k][2], dependencies[k][0], dependencies[k][1]));\n
                    }\n
                  }\n
                }\n
              } else {\n
                cell.setValue(cE.parseFormulaStatic(this.formula));\n
              }\n
            }\n
          }\n
          return false;\n
        }\n
      },\n
      makeCellVisit: function(tableI, row, col) {\n
        var fn = function() { \n
          return cE.visitCell(tableI, row, col);\n
        };\n
        fn.row = row;\n
        fn.col = col;\n
        return fn;\n
      },\n
      cell: function() {\n
        prototype: {// Cells don\'t know their coordinates, to make shifting easier.\n
          getError =      function()   { return this.error; },\n
          getValue =      function()   { return this.value; },\n
          setValue =      function(v, e) { this.value = v; this.error = e; },\n
          getFormula   =    function()  { return this.formula; },  // Like "=1+2+3" or "\'hello" or "1234.5"\n
          setFormula   =    function(v) { this.formula = v; },\n
          getFormulaFunc =  function()  { return this.formulaFunc; },\n
          setFormulaFunc =  function(v) { this.formulaFunc = v; },\n
          toString =      function() { return "Cell:[" + this.getFormula() + ": " + this.getValue() + ": " + this.getError() + "]"; };\n
        }\n
      }, // Prototype setup is later.\n
      columnLabelIndex: function(str) {\n
        // Converts A to 1, B to 2, Z to 26, AA to 27.\n
        var num = 0;\n
        for (var i = 0; i \074 str.length; i++) {\n
          var digit = str.toUpperCase().charCodeAt(i) - 65 + 1;    // 65 == \'A\'.\n
          num = (num * 26) + digit;\n
        }\n
        return num;\n
      },\n
      parseLocation: function(locStr) { // With input of "A1", "B4", "F20",\n
        if (locStr != null \046\046                 // will return [1,1], [4,2], [20,6].\n
          locStr.length \076 0 \046\046\n
          locStr != "\046nbsp;") {\n
          for (var firstNum = 0; firstNum \074 locStr.length; firstNum++) {\n
            if (locStr.charCodeAt(firstNum) \074= 57) {// 57 == \'9\'\n
              break;\n
            }\n
          }\n
          return [ parseInt(locStr.substring(firstNum)),\n
               cE.columnLabelIndex(locStr.substring(0, firstNum)) ];\n
        } else {\n
          return null;\n
        }\n
      },\n
      columnLabelString: function(index) {\n
        // The index is 1 based.  Convert 1 to A, 2 to B, 25 to Y, 26 to Z, 27 to AA, 28 to AB.\n
        // TODO: Got a bug when index \076 676.  675==YZ.  676==YZ.  677== AAA, which skips ZA series.\n
        //     In the spirit of billg, who needs more than 676 columns anyways?\n
        var b = (index - 1).toString(26).toUpperCase();   // Radix is 26.\n
        var c = [];\n
        for (var i = 0; i \074 b.length; i++) {\n
          var x = b.charCodeAt(i);\n
          if (i \074= 0 \046\046 b.length \076 1) {          // Leftmost digit is special, where 1 is A.\n
            x = x - 1;\n
          }\n
          if (x \074= 57) {                  // x \074= \'9\'.\n
            c.push(String.fromCharCode(x - 48 + 65)); // x - \'0\' + \'A\'.\n
          } else {\n
            c.push(String.fromCharCode(x + 10));\n
          }\n
        }\n
        return c.join("");\n
      },\n
      regEx: {\n
        n:          /[\\$,\\s]/g,\n
        cell:         /\\$?([a-zA-Z]+)\\$?([0-9]+)/g, //A1\n
        range:        /\\$?([a-zA-Z]+)\\$?([0-9]+):\\$?([a-zA-Z]+)\\$?([0-9]+)/g, //A1:B4\n
        remoteCell:     /\\$?(SHEET+)\\$?([0-9]+):\\$?([a-zA-Z]+)\\$?([0-9]+)/g, //SHEET1:A1\n
        remoteCellRange:  /\\$?(SHEET+)\\$?([0-9]+):\\$?([a-zA-Z]+)\\$?([0-9]+):\\$?([a-zA-Z]+)\\$?([0-9]+)/g, //SHEET1:A1:B4\n
        sheet:        /SHEET/,\n
        cellInsensitive:        /\\$?([a-zA-Z]+)\\$?([0-9]+)/gi, //a1\n
        rangeInsensitive:         /\\$?([a-zA-Z]+)\\$?([0-9]+):\\$?([a-zA-Z]+)\\$?([0-9]+)/gi, //a1:a4\n
        remoteCellInsensitive:      /\\$?(SHEET+)\\$?([0-9]+):\\$?([a-zA-Z]+)\\$?([0-9]+)/gi, //sheet1:a1\n
        remoteCellRangeInsensitive:   /\\$?(SHEET+)\\$?([0-9]+):\\$?([a-zA-Z]+)\\$?([0-9]+):\\$?([a-zA-Z]+)\\$?([0-9]+)/gi, //sheet1:a1:b4\n
        sheetInsensitive: /SHEET/i,\n
        amp:        /\046/g,\n
        gt:         /\074/g,\n
        lt:         /\076/g,\n
        nbsp:         /\046nbsp;/g\n
      },\n
      str: {\n
        amp:  \'\046amp;\',\n
        lt:   \'\046lt;\',\n
        gt:   \'\046gt;\',\n
        nbsp:   \'\046nbps;\'\n
      },\n
      parseFormula: function(formula, dependencies, thisTableI) { // Parse formula (without "=" prefix) like "123+SUM(A1:A6)/D5" into JavaScript expression string.\n
        var nrows = null;\n
        var ncols = null;\n
        if (cE.calcState.cellProvider != null) {\n
          nrows = cE.calcState.cellProvider.nrows;\n
          ncols = cE.calcState.cellProvider.ncols;\n
        }\n
        \n
        //Cell References Range - Other Tables\n
        formula = formula.replace(cE.regEx.remoteCellRange, \n
          function(ignored, TableStr, tableI, startColStr, startRowStr, endColStr, endRowStr) {\n
            var res = [];\n
            var startCol = cE.columnLabelIndex(startColStr);\n
            var startRow = parseInt(startRowStr);\n
            var endCol   = cE.columnLabelIndex(endColStr);\n
            var endRow   = parseInt(endRowStr);\n
            if (ncols != null) {\n
              endCol = Math.min(endCol, ncols);\n
            }\n
            if (nrows != null) {\n
              endRow = Math.min(endRow, nrows);\n
            }\n
            for (var r = startRow; r \074= endRow; r++) {\n
              for (var c = startCol; c \074= endCol; c++) {\n
                res.push("SHEET" + (tableI) + ":" + cE.columnLabelString(c) + r);\n
              }\n
            }\n
            return "[" + res.join(",") + "]";\n
          }\n
        );\n
        \n
        //Cell References Fixed - Other Tables\n
        formula = formula.replace(cE.regEx.remoteCell, \n
          function(ignored, tableStr, tableI, colStr, rowStr) {\n
            tableI = parseInt(tableI) - 1;\n
            colStr = colStr.toUpperCase();\n
            if (dependencies != null) {\n
              dependencies[\'SHEET\' + (tableI) + \':\' + colStr + rowStr] = [parseInt(rowStr), cE.columnLabelIndex(colStr), tableI];\n
            }\n
            return "(cE.calcState.cellProvider.getCell((" + (tableI) + "),(" + (rowStr) + "),\\"" + (colStr) + "\\").getValue())";\n
          }\n
        );\n
        \n
        //Cell References Range\n
        formula = formula.replace(cE.regEx.range, \n
          function(ignored, startColStr, startRowStr, endColStr, endRowStr) {\n
            var res = [];\n
            var startCol = cE.columnLabelIndex(startColStr);\n
            var startRow = parseInt(startRowStr);\n
            var endCol   = cE.columnLabelIndex(endColStr);\n
            var endRow   = parseInt(endRowStr);\n
            if (ncols != null) {\n
              endCol = Math.min(endCol, ncols);\n
            }\n
            if (nrows != null) {\n
              endRow = Math.min(endRow, nrows);\n
            }\n
            for (var r = startRow; r \074= endRow; r++) {\n
              for (var c = startCol; c \074= endCol; c++) {\n
                res.push(cE.columnLabelString(c) + r);\n
              }\n
            }\n
            return "[" + res.join(",") + "]";\n
          }\n
        );\n
        \n
        //Cell References Fixed\n
        formula = formula.replace(cE.regEx.cell, \n
          function(ignored, colStr, rowStr) {\n
            colStr = colStr.toUpperCase();\n
            if (dependencies != null) {\n
              dependencies[\'SHEET\' + thisTableI + \':\' + colStr + rowStr] = [parseInt(rowStr), cE.columnLabelIndex(colStr), thisTableI];\n
            }\n
            return "(cE.calcState.cellProvider.getCell((" + thisTableI + "),(" + (rowStr) + "),\\"" + (colStr) + "\\").getValue())";\n
          }\n
        );\n
        return formula;\n
      },  \n
      parseFormulaStatic: function(formula) { // Parse static formula value like "123.0" or "hello" or "\'hello world" into JavaScript value.\n
        if (formula == null) {\n
          return null;\n
        } else {\n
          var formulaNum = formula.replace(cE.regEx.n, \'\');\n
          var value = parseFloat(formulaNum);\n
          if (isNaN(value)) {\n
            value = parseInt(formulaNum);\n
          }\n
          if (isNaN(value)) {\n
            value = (formula.charAt(0) == "\\\'" ? formula.substring(1): formula);\n
          }\n
          return value;\n
        }\n
      },\n
      formula: null,\n
      formulaFunc: null,\n
      thisCell: null,\n
      makeFormulaEval: function(cell, row, col, formulaFunc) {\n
        cE.thisCell = cell;\n
        var fn = function() {\n
          var v = "";\n
          \n
          try {\n
            v = formulaFunc();\n
            /*\n
            switch(typeof(v)) {\n
              case "string":\n
                v = v\n
                  .replace(cE.regEx.amp, cE.str.amp)\n
                  .replace(cE.regEx.lt, cE.str.lt)\n
                  .replace(cE.regEx.gt, cE.str.gt)\n
                  .replace(cE.regEx.nbsp, cE.str.nbsp);\n
            }\n
            */\n
            cell.setValue(v);\n
            \n
          } catch (e) {\n
            cE.makeError(cell, e);\n
          }\n
        };\n
        fn.row = row;\n
        fn.col = col;\n
        return fn;\n
      },\n
      makeError: function(cell, e) {\n
        var msg = cE.ERROR + \': \' + msg;\n
        e.message.replace(/\\d+\\.?\\d*, \\d+\\.?\\d*/, function(v, i) {\n
          try {\n
            v = v.split(\', \');\n
            msg = (\'Cell:\' + cE.columnLabelString(parseInt(v[0]) + 1) + (parseInt(v[1])) + \' not found\');\n
          } catch (e) {}\n
        });\n
        cell.setValue(msg);\n
      },\n
      checkCycles: function(row, col, tableI) {\n
        for (var i = 0; i \074 cE.calcState.stack.length; i++) {\n
          var item = cE.calcState.stack[i];\n
          if (item.row != null \046\046 \n
            item.col != null \046\046\n
            item.row == row  \046\046\n
            item.col == col \046\046\n
            tableI == cE.calcState.i\n
          ) {\n
            return true;\n
          }\n
        }\n
        return false;\n
      }\n
    };\n
    \n
    var $window = jQuery(window);\n
    \n
    //initialize this instance of sheet\n
    jS.s = s;\n
    \n
    s.fnBefore();\n
    \n
    var o; var emptyFN = function() {};\n
    if (s.buildSheet) {//override urlGet, this has some effect on how the topbar is sized\n
      if (typeof(s.buildSheet) == \'object\') {\n
        o = s.buildSheet;\n
      } else if (s.buildSheet == true || s.buildSheet == \'true\') {\n
        o = jQuery(s.parent.html());\n
      } else if (s.buildSheet.match(/x/i)) {\n
        o = jQuery.sheet.makeTable.fromSize(s.buildSheet);\n
      }\n
    }\n
    \n
    //We need to take the sheet out of the parent in order to get an accurate reading of it\'s height and width\n
    //jQuery(this).html(s.loading);\n
    s.parent\n
      .html(\'\')\n
      .addClass(jS.cl.parent);\n
    \n
    //Use the setting height/width if they are there, otherwise use parent\'s\n
    s.width = (s.width ? s.width : s.parent.width());\n
    s.height = (s.height ? s.height : s.parent.height());\n
    \n
    \n
    // Drop functions if they are not needed \046 save time in recursion\n
    if (s.log) {\n
      s.parent.after(\'\074textarea id="\' + jS.id.log + \'" class="\' + jS.cl.log + \'" /\076\');\n
    } else {\n
      jS.log = emptyFN;\n
    }\n
    \n
    if (!s.showErrors) {\n
      cE.makeError = emptyFN;\n
    }\n
    \n
    if (!jQuery.support.boxModel) {\n
      s.boxModelCorrection = 0;\n
    }\n
    \n
    if (!jQuery.scrollTo) {\n
      jS.followMe = emptyFN;\n
    }\n
    \n
    jS.log(\'Startup\');\n
    \n
    $window\n
    .resize(function() {\n
      if (jS) { //We check because jS might have been killed\n
        s.width = s.parent.width();\n
        s.height = s.parent.height();\n
        jS.sheetSyncSize();\n
      }\n
    });\n
    \n
    //Extend the calculation engine plugins\n
    cE.fn = jQuery.extend(cE.fn, s.calculations);\n
    \n
    //Extend the calculation engine with advanced functions\n
    if (jQuery.sheet.advancedfn) {\n
      cE.fn = jQuery.extend(cE.fn, jQuery.sheet.advancedfn);\n
    }\n
    \n
    //Extend the calculation engine with finance functions\n
    if (jQuery.sheet.financefn) {\n
      cE.fn = jQuery.extend(cE.fn, jQuery.sheet.financefn);\n
    }\n
    \n
    //this makes cells and functions case insensitive\n
    if (s.caseInsensitive) {\n
      cE.regEx.cell = cE.regEx.cellInsensitive;\n
      cE.regEx.range = cE.regEx.rangeInsensitive;\n
      cE.regEx.remoteCell = cE.regEx.remoteCellInsensitive;\n
      cE.regEx.remoteCellRange = cE.regEx.remoteCellRangeInsensitive;\n
      cE.regEx.sheet = cE.regEx.sheetInsensitive;\n
      \n
      //Make sheet functions upper and lower case compatible\n
      for (var k in cE.fn) {\n
        var kLower = k.toLowerCase();\n
        if (kLower != k) {\n
          cE.fn[kLower] = cE.fn[k];\n
        }\n
      }\n
    }\n
    \n
    jS.openSheet(o, s.forceColWidthsOnStartup);\n
    \n
    return jS;\n
  },\n
  makeTable : {\n
    xml: function (data) { /* creates a table from xml, note: will not accept CDATA tags\n
                data: object, xml object;\n
                */\n
      var tables = jQuery(\'\074div /\076\');\n
    \n
      jQuery(data).find(\'document\').each(function(i) { //document\n
        var table = jQuery(\'\074table /\076\');\n
        var tableWidth = 0;\n
        var colgroup = jQuery(\'\074colgroup /\076\').appendTo(table);\n
        var tbody = jQuery(\'\074tbody /\076\');\n
      \n
        var metaData = jQuery(this).find(\'metadata\');\n
        var columnCount = metaData.find(\'columns\').text();\n
        var rowCount = metaData.find(\'rows\').text();\n
        var title = jQuery(this).attr(\'title\');\n
        var data = jQuery(this).find(\'data\');\n
        var col_widths = metaData.find(\'col_widths\').children();\n
        \n
        //go ahead and make the cols for colgroup\n
        for (var i = 0; i \074 parseInt(jQuery.trim(columnCount)); i++) {\n
          var w = parseInt(col_widths.eq(i).text().replace(\'px\', \'\'));\n
          w = (w ? w : 120); //if width doesn\'t exist, grab default\n
          tableWidth += w;\n
          colgroup.append(\'\074col width="\' + w + \'px" style="width: \' + w + \'px;" /\076\');\n
        }\n
        \n
        table\n
          .width(tableWidth)\n
          .attr(\'title\', title);\n
        \n
        for (var i = 0; i \074 rowCount; i++) { //rows\n
          var tds = data.find(\'r\' + i);\n
          var height = (data.attr(\'h\') + \'\').replace(\'px\', \'\');\n
          height = parseInt(height);\n
          \n
          var thisRow = jQuery(\'\074tr height="\' + (height ? height : 18) + \'px" /\076\');\n
          \n
          for (var j = 0; j \074 columnCount; j++) { //cols, they need to be counted because we don\'t send them all on export\n
            var newTd = \'\074td /\076\'; //we give td a default empty td\n
            var td = tds.find(\'c\' + j);\n
            \n
            if (td) {\n
              var text = td.text() + \'\';\n
              var cl = td.attr(\'class\');\n
              var style = td.attr(\'style\');\n
              var colSpan = td.attr(\'colspan\');\n
              \n
              var formula = \'\';\n
              if (text.charAt(0) == \'=\') {\n
                formula = \' formula="\' + text + \'"\';\n
              }\n
              \n
              newTd = \'\074td\' + formula + \n
                (style ? \' style=\\"\' + style + \'\\"\' : \'\') + \n
                (cl ? \' class=\\"\' + cl + \'\\"\' : \'\') +\n
                (colSpan ? \' colspan=\\"\' + colSpan + \'\\"\' : \'\') +\n
                (height ? \' height=\\"\' + height + \'px\\"\' : \'\') +\n
              \'\076\' + text + \'\074/td\076\';\n
            }\n
            thisRow.append(newTd);\n
          } \n
          tbody.append(thisRow);\n
        }\n
        table\n
          .append(tbody)\n
          .appendTo(tables);\n
      });\n
      \n
      return tables.children();\n
    },\n
    json: function(data, makeEval) { /* creates a sheet from json data, for format see top\n
                      data: json;\n
                      makeEval: bool, if true evals json;\n
                    */\n
      sheet = (makeEval == true ? eval(\'(\' + data + \')\') : data);\n
      \n
      var tables = jQuery(\'\074div /\076\');\n
      \n
      for (var i = 0; i \074 sheet.length; i++) {\n
        var colCount = parseInt(sheet[i].metadata.columns);\n
        var rowCount = parseInt(sheet[i].metadata.rows);\n
        title = sheet[i].metadata.title;\n
        title = (title ? title : "Spreadsheet " + i);\n
      \n
        var table = jQuery("\074table /\076");\n
        var tableWidth = 0;\n
        var colgroup = jQuery(\'\074colgroup /\076\').appendTo(table);\n
        var tbody = jQuery(\'\074tbody /\076\');\n
        \n
        //go ahead and make the cols for colgroup\n
        if (sheet[i][\'metadata\'][\'col_widths\']) {\n
          for (var x = 0; x \074 colCount; x++) {\n
            var w = 120;\n
            if (sheet[i][\'metadata\'][\'col_widths\'][\'c\' + x]) {\n
              var newW = parseInt(sheet[i][\'metadata\'][\'col_widths\'][\'c\' + x].replace(\'px\', \'\'));\n
              w = (newW ? newW : 120); //if width doesn\'t exist, grab default\n
              tableWidth += w;\n
            }\n
            colgroup.append(\'\074col width="\' + w + \'px" style="width: \' + w + \'px;" /\076\');\n
          }\n
        }\n
        \n
        table\n
          .attr(\'title\', title)\n
          .width(tableWidth);\n
        \n
        for (var x = 0; x \074 rowCount; x++) { //tr\n
          var tr = jQuery(\'\074tr /\076\').appendTo(table);\n
          tr.attr(\'height\', (sheet[i][\'data\'][\'r\' + x].h ? sheet[i][\'data\'][\'r\' + x].h : 18));\n
          \n
          for (var y = 0; y \074 colCount; y++) { //td\n
            var cell = sheet[i][\'data\'][\'r\' + x][\'c\' + y];\n
            var cur_val;\n
            var colSpan;\n
            var style;\n
            var cl;\n
            \n
            if (cell) {\n
              cur_val = cell.value + \'\';\n
              colSpan = cell.colSpan + \'\';\n
              style = cell.style + \'\';\n
              cl = cell.cl + \'\';\n
            }\n
\n
            var cur_td = jQuery(\'\074td\' + \n
                (style ? \' style=\\"\' + style + \'\\"\' : \'\' ) + \n
                (cl ? \' class=\\"\' + cl + \'\\"\' : \'\' ) + \n
                (colSpan ? \' colspan=\\"\' + colSpan + \'\\"\' : \'\' ) + \n
              \' /\076\');\n
            try {\n
              if(typeof(cur_val) == "number") {\n
                cur_td.html(cur_val);\n
              } else {\n
                if (cur_val.charAt(0) == \'=\') {\n
                  cur_td.attr("formula", cur_val);\n
                } else {\n
                  cur_td.html(cur_val);\n
                }\n
              }\n
            } catch (e) {}\n
          \n
            tr.append(cur_td);\n
\n
          }\n
        }\n
        \n
        tables.append(table);\n
      }\n
      return tables.children();\n
    },\n
    fromSize: function(size, h, w) { /* creates a spreadsheet object from a size given \n
                      size: string, example "10x100" which means 10 columns by 100 rows;\n
                      h: int, height for each new row;\n
                      w: int, width of each new column;\n
                    */\n
      if (!size) {\n
        size = "5x10";\n
      }\n
      size = size.toLowerCase().split(\'x\');\n
\n
      var columnsCount = parseInt(size[0]);\n
      var rowsCount = parseInt(size[1]);\n
      \n
      //Create elements before loop to make it faster.\n
      var newSheet = jQuery(\'\074table /\076\');\n
      var standardTd = \'\074td\076\074/td\076\';\n
      var tds = \'\';\n
      \n
      //Using -- is many times faster than ++\n
      for (var i = columnsCount; i \076= 1; i--) {\n
        tds += standardTd;\n
      }\n
\n
      var standardTr = \'\074tr\' + (h ? \' height="\' + h + \'px" style="height: \' + h + \'px;"\' : \'\') + \'\076\' + tds + \'\074/tr\076\';\n
      var trs = \'\';\n
      for (var i = rowsCount; i \076= 1; i--) {\n
        trs += standardTr;\n
      }\n
      \n
      newSheet.html(\'\074tbody\076\' + trs + \'\074/tbody\076\');\n
      \n
      if (w) {\n
        newSheet.width(columnsCount * w);\n
      }\n
      \n
      return newSheet;\n
    }\n
  },\n
  killAll: function() { /* removes all sheets */\n
    if (jQuery.sheet) {\n
      if (jQuery.sheet.instance) {\n
        for (var i = 0; i \074 jQuery.sheet.instance.length; i++) {\n
          if (jQuery.sheet.instance[i]) {\n
            if (jQuery.sheet.instance[i].kill) {\n
              jQuery.sheet.instance[i].kill();\n
            }\n
          }\n
        }\n
      }\n
    }\n
  },\n
  paneScrollLocker: function(obj, I) { //This can be used with setting fnPaneScroll to lock all loaded sheets together when scrolling, useful in history viewing\n
    jQuery(jQuery.sheet.instance).each(function(i) {\n
      this.obj.pane()\n
        .scrollLeft(obj.scrollLeft())\n
        .scrollTop(obj.scrollTop());\n
    });\n
  },\n
  switchSheetLocker: function(I) { //This can be used with setting fnSwitchSheet to locks sheets together when switching, useful in history viewing\n
    jQuery(jQuery.sheet.instance).each(function(i) {\n
      this.setActiveSheet(I);\n
    });\n
  }\n
};\n
\n
var key = { /* key objects, makes it easier to develop */\n
  BACKSPACE:      8,\n
  CAPS_LOCK:      20,\n
  COMMA:        188,\n
  CONTROL:      17,\n
  ALT:        18,\n
  DELETE:       46,\n
  DOWN:         40,\n
  END:        35,\n
  ENTER:        13,\n
  ESCAPE:       27,\n
  HOME:         36,\n
  INSERT:       45,\n
  LEFT:         37,\n
  NUMPAD_ADD:     107,\n
  NUMPAD_DECIMAL:   110,\n
  NUMPAD_DIVIDE:    111,\n
  NUMPAD_ENTER:     108,\n
  NUMPAD_MULTIPLY:  106,\n
  NUMPAD_SUBTRACT:  109,\n
  PAGE_DOWN:      34,\n
  PAGE_UP:      33,\n
  PERIOD:       190,\n
  RIGHT:        39,\n
  SHIFT:        16,\n
  SPACE:        32,\n
  TAB:        9,\n
  UP:         38,\n
  F:          70,\n
  V:          86,\n
  Y:          89,\n
  Z:          90\n
};\n
\n
var arrHelpers = {\n
  foldPrepare: function(firstArg, theArguments, unique) { // Computes the best array-like arguments for calling fold().\n
    var result;\n
    if (firstArg != null \046\046\n
      firstArg instanceof Object \046\046\n
      firstArg["length"] != null) {\n
      result = firstArg;\n
    } else {\n
      result = theArguments;\n
    }\n
    \n
    if (unique) {\n
      result = this.unique(result);\n
    }\n
    \n
    return result;\n
  },\n
  fold: function(arr, funcOfTwoArgs, result, castToN, N) {\n
    for (var i = 0; i \074 arr.length; i++) {\n
      result = funcOfTwoArgs(result, (castToN == true ? N(arr[i]): arr[i]));\n
    }\n
    return result;\n
  },\n
  toNumbers: function(arr) {\n
    arr = jQuery.makeArray(arr);\n
    \n
    for (var i = 0; i \074 arr.length; i++) {\n
      if (jQuery.isArray(arr[i])) {\n
        arr[i] = this.toNumbers(arr[i]);\n
      } else if (arr[i]) {\n
        if (isNaN(arr[i])) {\n
          arr[i] = 0;\n
        }\n
      } else {\n
        arr[i] = 0;\n
      }\n
    }\n
    \n
    return arr;\n
  },\n
  unique: function(arr) {\n
    var a = [];\n
    var l = arr.length;\n
    for (var i=0; i\074l; i++) {\n
      for(var j=i+1; j\074l; j++) {\n
        // If this[i] is found later in the array\n
        if (arr[i] === arr[j])\n
          j = ++i;\n
      }\n
      a.push(arr[i]);\n
    }\n
    return a;\n
  }\n
};\n
\n
jQuery.fn.extend({ \n
        disableSelection : function() { \n
                this.each(function() { \n
                        this.onselectstart = function() { return false; }; \n
                        this.unselectable = "on"; \n
                        jQuery(this).css(\'-moz-user-select\', \'none\'); \n
                }); \n
        } \n
});\n
</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
