/**
 * MegaTable
 * Load infinite sized tables in the browser with a fixed number of elements
 * @constructor
 */
var MegaTable = (function(document) {
  "use strict";

  var charSize = function() {
    var characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
      el = document.createElement('span'),
      size;

    el.innerHTML = characters;
    document.body.appendChild(el);

    size = {
      width: el.offsetWidth / characters.length,
      height: el.offsetHeight
    };

    el.parentNode.removeChild(el);

    return size;
  };

  /**
   *
   * @param {Object} settings inherits values from MegaTable.defaultSettings
   * @constructor
   */
  function MegaTable(settings) {
    var table = this.table = document.createElement('table'),
      colGroup = this.colGroup = document.createElement('colGroup'),
      tBody = this.tBody = document.createElement('tBody'),
      defaults = MegaTable.defaultSettings,
      i;

    this.charSize = charSize();

    for(i in defaults) if (defaults.hasOwnProperty(i)) {
      if (settings[i] === undefined) settings[i] = defaults[i];
    }

    this.rowIndex = 0;
    this.columnIndex = 0;

    this.trInsertionIndex = 0;
    this.thInsertionIndex = 0;

    this.rows = settings.rows;
    this.columns = settings.columns;
    this.updateCorner = settings.updateCorner;
    this.updateCell = settings.updateCell;
    this.updateRowHeader = settings.updateRowHeader;
    this.updateColumnHeader = settings.updateColumnHeader;

    table.appendChild(colGroup);
    table.appendChild(tBody);

    if (settings.strict) {
      table.style.tableLayout = 'fixed';
      table.style.width = '0px';
    }
    table.className = 'mega-table';

    this
      ._createMegaTableDOM()
      ._updateCorner();

    if (settings.element !== null) {
      settings.element.appendChild(table);
    }

    this.rowHeaders = 1;
    this.columnHeaders = 1;

    this.initiated = true;
  }

  MegaTable.prototype = {
    /**
     *
     * @param {Number} trIndex
     * @returns {MegaTable}
     */
    setRowStartIndex: function(trIndex) {
      if (trIndex < 0) {
        trIndex = 0;
      } else if (trIndex > this.rows) {
        trIndex = this.rows;
      }

      this.trInsertionIndex = trIndex;

      return this;
    },
    /**
     *
     * @param {Number} columnIndex
     * @returns {MegaTable}
     */
    setColumnStartIndex: function(columnIndex) {
      if (columnIndex < 0) {
        columnIndex = 0;
      } else if (columnIndex > this.columns) {
        columnIndex = this.columns;
      }

      this.thInsertionIndex = columnIndex;

      return this;
    },
    /**
     *
     * @param {Number} rowIndex
     * @param {Number} columnIndex
     * @returns {MegaTable}
     */
    update: function (rowIndex, columnIndex) {
      return this
        .updateRows(rowIndex)
        .updateColumns(columnIndex);
    },

    /**
     * @param {Number} rowIndex
     * @returns {MegaTable}
     */
    updateRows: function (rowIndex) {
      var up = 0,
        down = 0,
        detachedRow;

      if (this.rowIndex > rowIndex) {
        up = this.rowIndex - rowIndex;

        if (up > this.rows) {
          up -= this.rows;
          this.rowIndex = rowIndex + up;
        }
      } else if (this.rowIndex < rowIndex) {
        down = rowIndex - this.rowIndex;

        if (down > this.rows) {
          down -= this.rows;
          this.rowIndex = rowIndex - down;
        }
      }

      if (up > 0) {
        while (up > 0) {
          this.rowIndex--;
          detachedRow = this._moveBottomRowHeaderToTop();
          this._moveBottomRowToTop(detachedRow);
          up--;
        }
        this._updateCorner();
      }

      else if (down > 0) {
        while (down > 0) {
          this.rowIndex++;
          detachedRow = this._moveTopRowHeaderToBottom();
          this._moveTopRowToBottom(detachedRow);
          down--;
        }
        this._updateCorner();
      }

      return this;
    },

    /**
     *
     * @param {Number} columnIndex
     * @returns {MegaTable}
     */
    updateColumns: function (columnIndex) {
      var left = 0,
        right = 0;

      if (this.columnIndex > columnIndex) {
        left = this.columnIndex - columnIndex;

        if (left > this.columns) {
          left -= this.columns;
          this.columnIndex = columnIndex + left;
        }
      } else if (this.columnIndex < columnIndex) {
        right = columnIndex - this.columnIndex;

        if (right > this.columns) {
          right -= this.columns;
          this.columnIndex = columnIndex - right;
        }
      }

      if (left > 0) {
        this.table.style.visibility = 'hidden';
        while (left > 0) {
          this.columnIndex--;

          this
            ._moveRightColumnHeaderToLeft()
            ._moveRightColumnToLeft();

          left--;
        }
        this.table.style.visibility = '';
      }

      else if (right > 0) {
        this.table.style.visibility = 'hidden';
        while (right > 0) {
          this.columnIndex++;

          this
            ._moveLeftColumnHeaderToRight()
            ._moveLeftColumnToRight();

          right--;
        }
        this.table.style.visibility = '';
      }

      return this;
    },

    /**
     *
     * @param {Number} trIndex
     * @returns {MegaTable}
     */
    newRow: function(trIndex) {
      var row = this._moveBottomRowHeaderToIndex(trIndex);
      return this
        ._moveBottomRowToIndex(row, trIndex)
        ._updateRowHeadersFollowing(trIndex)
        ._updateRowCellsFollowing(trIndex);
    },

    /**
     *
     * @param {Number} thIndex
     * @returns {MegaTable}
     */
    newColumn: function(thIndex) {
      return this
        ._moveRightColumnHeaderToIndex(thIndex)
        ._moveRightColumnToIndex(thIndex)
        ._updateColumnHeadersFollowing(thIndex)
        ._updateColumnCellsFollowing(thIndex);
    },

    /**
     *
     * @param {Number} rowIndex
     * @returns {MegaTable}
     */
    removeRow: function(rowIndex) {
      var row = this._moveIndexRowHeaderToBottom(rowIndex);
      return this
        ._moveIndexRowToBottom(row)
        ._updateRowHeadersFollowing(this.rows)
        ._updateRowCellsFollowing(this.rows);
    },

    /**
     *
     * @param {Number} thIndex
     * @returns {*|MegaTable}
     */
    removeColumn: function(thIndex) {

      this._updateColumnHeadersFollowing(thIndex);
      this._updateColumnCellsFollowing(thIndex);
      return this;
    },
    /**
     *
     * @param {Number} [trIndex]
     * @returns {MegaTable}
     */
    forceRedrawRows: function(trIndex) {
      trIndex = trIndex || 0;

      this.table.style.visibility = 'hidden';

      this
        ._updateRowHeadersFollowing(trIndex)
        ._updateRowCellsFollowing(trIndex);

      this.table.style.visibility = '';

      return this;
    },
  
    /**
     *
     * @param {Number} [thIndex]
     * @returns {MegaTable}
     */
    forceRedrawColumns: function (thIndex) {
      thIndex = thIndex || 0;

      this.table.style.visibility = 'hidden';

      this
        ._updateColumnHeadersFollowing(thIndex)
        ._updateColumnCellsFollowing(thIndex);

      this.table.style.visibility = '';

      return this;
    },

    /**
     *
     * @param {Number} i
     * @returns {HTMLElement}
     */
    col: function(i) {
      return this.colGroup.children[i];
    },
  
    //below used in instantiation
  
    /**
     * @param {HTMLTableRowElement} tr
     * @returns {MegaTable}
     * @private
     */
    _createCornerDOM: function (tr) {
      var th = this.cornerTh = document.createElement('th'),
        col = this.cornerCol = document.createElement('col');

      col.style.width = '14px';

      tr.appendChild(th);

      this.updateCorner(th, col);

      this.colGroup.appendChild(col);

      return this;
    },

    /**
     *
     * @returns {MegaTable}
     * @private
     */
    _createColumnHeaderDOM: function () {
      var tr = document.createElement('tr'),
        colGroup = this.colGroup,
        columnIndex = 0,
        th,
        col;

      this._createCornerDOM(tr);

      this.tBody.appendChild(tr);

      for (; columnIndex < this.columns; columnIndex++) {
        th = document.createElement('th');
        tr.appendChild(th);
        col = document.createElement('col');
        colGroup.appendChild(col);

        this.updateColumnHeader(this.columnIndex + columnIndex, th, col);
      }

      return this;
    },

    /**
     *
     * @param {HTMLTableElement} tr
     * @param {Number} i
     * @returns {MegaTable}
     * @private
     */
    _createRowHeaderDOM: function (tr, i) {
      var th = document.createElement('th');
      tr.appendChild(th);
      this.updateRowHeader(i, th);

      return this;
    },

    /**
     *
     * @returns {MegaTable}
     * @private
     */
    _createMegaTableDOM: function () {
      var tBody = this.tBody,
        rowIndex = this.rowIndex,
        rowIndex = 0,
        columnIndex = 0,
        tr,
        td;

      this._createColumnHeaderDOM();

      for (; rowIndex < this.rows; rowIndex++) {
        columnIndex = 0;
        tr = document.createElement('tr');

        this._createRowHeaderDOM(tr, this.rowIndex + rowIndex);

        tBody.appendChild(tr);
        for (; columnIndex < this.columns; columnIndex++) {
          td = document.createElement('td');
          tr.appendChild(td);
          this.updateCell(this.rowIndex + rowIndex, columnIndex, td);
        }
      }

      return this;
    },



    //used in updating

    /**
     *
     * @returns {MegaTable}
     * @private
     */
    _updateCorner: function() {
      var tBody = this.tBody,
        col = this.cornerCol,
        targetRow = tBody.lastChild,
        th = targetRow.firstChild,
        newWidth,
        minWidth = 20,
        text;

      if (th.innerText !== null && th.innerText !== undefined) {
        text = th.innerText;
      } else if (th.textContent !== null && th.textContent !== undefined) {
        text = th.textContent;
      }

      newWidth = this.charSize.width * text.length;
      //set a minimum width, because css doesn't respect this on col in FF
      newWidth = (newWidth > minWidth ? newWidth : minWidth);

      if (newWidth !== col._width || col._width === undefined) {
        col._width = newWidth;
        col.style.width = newWidth + 'px';
      }

      return this;
    },

    /**
     *
     * @returns {MegaTable}
     * @private
     */
    _moveRightColumnHeaderToLeft: function() {
      var parent = this.tBody.children[0],
        colGroup = this.colGroup,
        col = colGroup.lastChild,
        header = parent.lastChild;

      parent.removeChild(header);
      colGroup.removeChild(col);

      while(header.lastChild !== null) {
        header.removeChild(header.lastChild);
      }

      if (header.hasAttribute('style')) header.removeAttribute('style');
      if (header.hasAttribute('class')) header.className = '';

      if (col.hasAttribute('style')) col.removeAttribute('style');
      if (col.hasAttribute('class')) col.className = '';

      this.updateColumnHeader(this.columnIndex, header, col, MegaTable.left);

      //insert after corner
      parent.insertBefore(header, parent.children[this.thInsertionIndex + this.rowHeaders]);
      colGroup.insertBefore(col, colGroup.children[this.thInsertionIndex + this.rowHeaders]);

      return this;
    },

    /**
     *
     * @param thIndex
     * @returns {MegaTable}
     * @private
     */
    _moveRightColumnHeaderToIndex: function(thIndex) {
      var parent = this.tBody.children[0],
        colGroup = this.colGroup,
        col = colGroup.lastChild,
        header = parent.lastChild;

      if (thIndex < this.thInsertionIndex) {
        thIndex = this.thInsertionIndex;
      } else if (thIndex > this.columns) {
        thIndex = this.columns;
      }

      parent.removeChild(header);
      colGroup.removeChild(col);

      while(header.lastChild !== null) {
        header.removeChild(header.lastChild);
      }

      if (header.hasAttribute('style')) header.removeAttribute('style');
      if (header.hasAttribute('class')) header.className = '';

      if (col.hasAttribute('style')) col.removeAttribute('style');
      if (col.hasAttribute('class')) col.className = '';

      this.updateColumnHeader(this.columnIndex + thIndex, header, col);

      //insert before corner
      parent.insertBefore(header, parent.children[thIndex + this.rowHeaders]);
      colGroup.insertBefore(col, colGroup.children[thIndex + this.rowHeaders]);

      return this;
    },

    /**
     *
     * @param thIndex
     * @returns {MegaTable}
     * @private
     */
    _moveIndexColumnHeaderToRight: function(thIndex) {
      if (thIndex > this.columns) {
        thIndex = this.columns;
      }

      var parent = this.tBody.children[0],
      colGroup = this.colGroup,
      col = colGroup.children[thIndex + this.rowHeaders],
      header = parent.children[thIndex + this.rowHeaders];

      parent.removeChild(header);
      colGroup.removeChild(col);

      while(header.lastChild !== null) {
        header.removeChild(header.lastChild);
      }

      if (header.hasAttribute('style')) header.removeAttribute('style');
      if (header.hasAttribute('class')) header.className = '';

      if (col.hasAttribute('style')) col.removeAttribute('style');
      if (col.hasAttribute('class')) col.className = '';

      this.updateColumnHeader(this.columnIndex + this.columns, header, col);

      //insert before corner
      parent.appendChild(header);
      colGroup.appendChild(col);

      return this;
    },

    /**
     *
     * @returns {MegaTable}
     * @private
     */
    _moveLeftColumnHeaderToRight: function() {
      var parent = this.tBody.children[0],
        colGroup = this.colGroup,
        col = colGroup.children[this.thInsertionIndex + this.rowHeaders],
        header = parent.children[this.thInsertionIndex + this.rowHeaders];

      parent.removeChild(header);
      colGroup.removeChild(col);

      while(header.lastChild !== null) {
        header.removeChild(header.lastChild);
      }

      if (header.hasAttribute('style')) header.removeAttribute('style');
      if (header.hasAttribute('class')) header.className = '';

      if (col.hasAttribute('style')) col.removeAttribute('style');
      if (col.hasAttribute('class')) col.className = '';

      this.updateColumnHeader(this.columnIndex + parent.children.length - 1, header, col, MegaTable.right);

      //insert at end
      parent.appendChild(header);
      colGroup.appendChild(col);

      return this;
    },

    /**
     *
     * @returns {HTMLTableRowElement|Node}
     * @private
     */
    _moveBottomRowHeaderToTop: function() {
      var parent = this.tBody,
        header = parent.lastChild.children[0];

      //we intentionally leave the node detached here because the body manages it
      parent.removeChild(header.parentNode);

      while(header.lastChild !== null) {
        header.removeChild(header.lastChild);
      }

      if (header.hasAttribute('style')) header.removeAttribute('style');
      if (header.hasAttribute('class')) header.className = '';

      this.updateRowHeader(this.rowIndex, header, MegaTable.up);

      return header.parentNode;
    },

    /**
     *
     * @param {Number} trIndex
     * @returns {Node}
     * @private
     */
    _moveBottomRowHeaderToIndex: function(trIndex) {
      var parent = this.tBody,
        row = parent.lastChild,
        header = row.children[0];

      if (trIndex < this.trInsertionIndex) {
        trIndex = this.trInsertionIndex;
      } else if (trIndex > this.rows) {
        trIndex = this.rows;
      }

      //we intentionally leave the node detached here because the body manages it
      parent.removeChild(row);

      while(header.lastChild !== null) {
        header.removeChild(header.lastChild);
      }

      if (header.hasAttribute('style')) header.removeAttribute('style');
      if (header.hasAttribute('class')) header.className = '';

      this.updateRowHeader(this.rowIndex + trIndex, header);

      return row;
    },

    /**
     *
     * @param {Number} rowIndex
     * @returns {Node|HTMLTableRowElement}
     * @private
     */
    _moveIndexRowHeaderToBottom: function(rowIndex) {
      if (rowIndex > this.rows) {
        rowIndex = this.rows;
      }

      var parent = this.tBody,
        row = parent.children[rowIndex],
        header = row.children[0];

      //we intentionally leave the node detached here because the body manages it
      parent.removeChild(row);

      while(header.lastChild !== null) {
        header.removeChild(header.lastChild);
      }

      if (header.hasAttribute('style')) header.removeAttribute('style');
      if (header.hasAttribute('class')) header.className = '';

      this.updateRowHeader(this.rowIndex + this.rows, header);

      return row;
    },

    /**
     *
     * @returns {HTMLTableRowElement|Node}
     * @private
     */
    _moveTopRowHeaderToBottom: function() {
      var parent = this.tBody,
        header = parent.children[this.trInsertionIndex + this.columnHeaders].children[0];

      //we intentionally leave the node detached here because the body manages it
      parent.removeChild(header.parentNode);

      while(header.lastChild !== null) {
        header.removeChild(header.lastChild);
      }

      if (header.hasAttribute('style')) header.removeAttribute('style');
      if (header.hasAttribute('class')) header.className = '';

      this.updateRowHeader(this.rowIndex + parent.children.length - 1, header, MegaTable.down);

      return header.parentNode;
    },

    /**
     *
     * @param {HTMLTableElement} row
     * @returns {MegaTable}
     * @private
     */
    _moveBottomRowToTop: function (row) {
      var children = row.children,
        element,
        columnIndex = this.thInsertionIndex;

      for (; columnIndex < this.columns; columnIndex++) {
        element = children[columnIndex + this.columnHeaders];

        while(element.firstChild !== null) {
          element.removeChild(element.firstChild);
        }

        if (element.hasAttribute('style')) element.removeAttribute('style');
        if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
        if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
        if (element.hasAttribute('class')) element.className = '';

        this.updateCell(this.rowIndex, this.columnIndex + columnIndex, element, MegaTable.up);
      }

      this.tBody.insertBefore(row, this.tBody.children[this.trInsertionIndex + this.columnHeaders]);

      return this;
    },

    /**
     *
     * @param {Node|HTMLTableRowElement} tr
     * @param {Number} trIndex
     * @returns {MegaTable}
     * @private
     */
    _moveBottomRowToIndex: function (tr, trIndex) {
      var children = tr.children,
        element,
        columnIndex = this.thInsertionIndex;

      if (trIndex < this.trInsertionIndex) {
        trIndex = this.trInsertionIndex;
      } else if (trIndex > this.rows) {
        trIndex = this.rows;
      }

      for (; columnIndex < this.columns; columnIndex++) {
        element = children[columnIndex + this.columnHeaders];

        while(element.firstChild !== null) {
          element.removeChild(element.firstChild);
        }

        if (element.hasAttribute('style')) element.removeAttribute('style');
        if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
        if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
        if (element.hasAttribute('class')) element.className = '';

        this.updateCell(this.rowIndex + trIndex, this.columnIndex + columnIndex, element);
      }

      this.tBody.insertBefore(tr, this.tBody.children[trIndex + this.columnHeaders]);

      return this;
    },

    /**
     *
     * @param {HTMLTableRowElement} row
     * @returns {MegaTable}
     * @private
     */
    _moveIndexRowToBottom: function (row) {
      var children = row.children,
        element,
        columnIndex = this.thInsertionIndex;

      for (; columnIndex < this.columns; columnIndex++) {
        element = children[columnIndex + this.columnHeaders];

        while(element.firstChild !== null) {
          element.removeChild(element.firstChild);
        }

        if (element.hasAttribute('style')) element.removeAttribute('style');
        if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
        if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
        if (element.hasAttribute('class')) element.className = '';

        this.updateCell(this.rowIndex + this.rows, this.columnIndex + columnIndex, element);
      }

      this.tBody.appendChild(row);

      return this;
    },

    /**
     *
     * @param {HTMLTableRowElement} row
     * @returns {MegaTable}
     * @private
     */
    _moveTopRowToBottom: function (row) {
      var children = row.children,
        element,
        columnIndex = this.thInsertionIndex;

      for (; columnIndex < this.columns; columnIndex++) {
        element = children[columnIndex + this.columnHeaders];

        while(element.firstChild !== null) {
          element.removeChild(element.firstChild);
        }

        if (element.hasAttribute('style')) element.removeAttribute('style');
        if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
        if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
        if (element.hasAttribute('class')) element.className = '';

        this.updateCell(this.rowIndex + this.tBody.children.length - 1, this.columnIndex + columnIndex, element, MegaTable.down);
      }

      this.tBody.insertBefore(row, null);

      return this;
    },

    /**
     *
     * @returns {MegaTable}
     * @private
     */
    _moveRightColumnToLeft: function () {
      var rows = this.tBody.children,
        row,
        element,
        rowIndex = this.trInsertionIndex;

      for (; rowIndex < this.rows; rowIndex++) {
        row = rows[rowIndex + this.rowHeaders];
        element = row.lastChild;
        row.removeChild(element);

        while(element.firstChild !== null) {
          element.removeChild(element.firstChild);
        }

        if (element.hasAttribute('style')) element.removeAttribute('style');
        if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
        if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
        if (element.hasAttribute('class')) element.className = '';

        this.updateCell(this.rowIndex + rowIndex, this.columnIndex, element, MegaTable.left);

        row.insertBefore(element, row.children[this.trInsertionIndex + this.rowHeaders]);
      }

      return this;
    },

    /**
     *
     * @param {Number} thIndex
     * @returns {MegaTable}
     * @private
     */
    _moveRightColumnToIndex: function (thIndex) {
      var rows = this.tBody.children,
        row,
        element,
        rowIndex = this.trInsertionIndex;

      if (thIndex < this.thInsertionIndex) {
        thIndex = this.thInsertionIndex;
      }

      for (; rowIndex < this.rows; rowIndex++) {
        row = rows[rowIndex + this.rowHeaders];
        element = row.lastChild;
        row.removeChild(element);

        while(element.firstChild !== null) {
          element.removeChild(element.firstChild);
        }

        if (element.hasAttribute('style')) element.removeAttribute('style');
        if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
        if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
        if (element.hasAttribute('class')) element.className = '';

        this.updateCell(this.rowIndex + rowIndex, this.columnIndex + thIndex, element);

        row.insertBefore(element, row.children[thIndex + this.rowHeaders]);
      }

      return this;
    },

    /**
     *
     * @param {Number} thIndex
     * @returns {MegaTable}
     * @private
     */
    _moveIndexColumnToRight: function (thIndex) {
      if (thIndex < this.columns) {
        thIndex = this.columns;
      }

      var rows = this.tBody.children,
        row,
        element,
        rowIndex = this.trInsertionIndex;

      for (; rowIndex < this.rows; rowIndex++) {
        row = rows[rowIndex + this.rowHeaders];
        element = row.children[thIndex];
        row.removeChild(element);

        while(element.firstChild !== null) {
          element.removeChild(element.firstChild);
        }

        if (element.hasAttribute('style')) element.removeAttribute('style');
        if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
        if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
        if (element.hasAttribute('class')) element.className = '';

        this.updateCell(this.rowIndex + rowIndex, this.columnIndex + this.columns, element);

        row.insertBefore(element, row.children[thIndex + this.rowHeaders]);
      }

      return this;
    },

    /**
     *
     * @returns {MegaTable}
     * @private
     */
    _moveLeftColumnToRight: function () {
      var rows = this.tBody.children,
        row,
        columnIndexEnd = this.columns,
        element,
        rowIndex = this.trInsertionIndex;

      for (; rowIndex < this.rows; rowIndex++) {
        row = rows[rowIndex + this.rowHeaders];
        element = row.children[this.thInsertionIndex + this.rowHeaders];
        row.removeChild(element);

        while(element.firstChild !== null) {
          element.removeChild(element.firstChild);
        }

        if (element.hasAttribute('style')) element.removeAttribute('style');
        if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
        if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
        if (element.hasAttribute('class')) element.className = '';

        this.updateCell(this.rowIndex + rowIndex, columnIndexEnd, element, MegaTable.right);

        row.appendChild(element);
      }

      return this;
    },

    /**
     *
     * @param {Number} trIndex
     * @returns {MegaTable}
     * @private
     */
    _updateRowHeadersFollowing: function(trIndex) {
      var rows = this.tBody.children,
        header;

      for(;trIndex < this.rows;trIndex++) {
        header = rows[trIndex + this.columnHeaders].children[0];

        while(header.firstChild !== null) {
          header.removeChild(header.firstChild);
        }

        if (header.hasAttribute('style')) header.removeAttribute('style');
        if (header.hasAttribute('class')) header.className = '';
        this.updateRowHeader(this.rowIndex + trIndex, header);
      }

      return this;
    },

    /**
     *
     * @param {Number} thIndex
     * @returns {MegaTable}
     * @private
     */
    _updateColumnHeadersFollowing: function(thIndex) {
      var headers = this.tBody.children[0].children,
        colGroup = this.colGroup,
        cols = colGroup.children,
        header,
        col;

      for(;thIndex < this.columns;thIndex++) {
        header = headers[thIndex + this.rowHeaders];
        col = cols[thIndex + this.rowHeaders];

        while(header.firstChild !== null) {
          header.removeChild(header.firstChild);
        }

        if (header.hasAttribute('style')) header.removeAttribute('style');
        if (header.hasAttribute('class')) header.className = '';

        if (col.hasAttribute('style')) col.removeAttribute('style');
        if (col.hasAttribute('class')) col.className = '';

        this.updateColumnHeader(this.columnIndex + thIndex, header, col);
      }

      return this;
    },

    /**
     *
     * @param {Number} trIndex
     * @returns {MegaTable}
     * @private
     */
    _updateRowCellsFollowing: function(trIndex) {
      var rows = this.tBody.children,
        columnIndex,
        element,
        row;

      if (trIndex < this.trInsertionIndex) {
        trIndex = this.trInsertionIndex;
      } else if (trIndex > this.rows) {
        trIndex = this.rows;
      }

      for (;trIndex < this.rows; trIndex++) {
        row = rows[trIndex + this.columnHeaders];
        columnIndex = this.thInsertionIndex;
        for (; columnIndex < this.columns; columnIndex++) {
          element = row.children[columnIndex + this.columnHeaders];

          while (element.firstChild !== null) {
            element.removeChild(element.firstChild);
          }

          if (element.hasAttribute('style')) element.removeAttribute('style');
          if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
          if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
          if (element.hasAttribute('class')) element.className = '';

          this.updateCell(this.rowIndex + trIndex, this.columnIndex + columnIndex, element);
        }
      }

      return this;
    },

    /**
     *
     * @param {Number} thIndex
     * @returns {MegaTable}
     * @private
     */
    _updateColumnCellsFollowing: function(thIndex) {
      var rows = this.tBody.children,
        rowIndex,
        element,
        row;

      if (thIndex < this.thInsertionIndex) {
        thIndex = this.thInsertionIndex;
      } else if (thIndex > this.columns) {
        thIndex = this.columns;
      }

      for (; thIndex < this.columns; thIndex++) {
        rowIndex = this.trInsertionIndex;
        for (;rowIndex < this.rows; rowIndex++) {
          row = rows[rowIndex + this.rowHeaders];

          element = row.children[thIndex + this.rowHeaders];

          while (element.firstChild !== null) {
            element.removeChild(element.firstChild);
          }

          if (element.hasAttribute('style')) element.removeAttribute('style');
          if (element.hasAttribute('colSpan')) element.removeAttribute('colSpan');
          if (element.hasAttribute('rowSpan')) element.removeAttribute('rowSpan');
          if (element.hasAttribute('class')) element.className = '';

          this.updateCell(this.rowIndex + rowIndex, this.columnIndex + thIndex, element);
        }
      }

      return this;
    }
  };

  /**
   *
   * @type {Object}
   */
  MegaTable.defaultSettings = {
    /**
     * element you want mega table in
     * @type {Element}
     */
    element: null,

    /**
     * number of rows you'd like your table to have
     * @type {Number}
     */
    rows: 10,

    /**
     * number of columns you'd like your table to have
     * @type {Number}
     */
    columns: 10,

    /**
     * turns on strict mode so that size comes strictly from col elements
     * @type {Boolean}
     */
    strict: false,

    updateCorner: function(th, col) {},

    /**
     * callback for when a table data element needs updated
     * @type {Function}
     * @param {Number} row
     * @param {Number} column
     * @param {HTMLTableCellElement} td
     * @param {Number} direction
     */
    updateCell: function(row, column, td, direction) {},

    /**
     * callback for when a table row header element needs updated
     * @type {Function}
     * @param {Number} i
     * @param {HTMLTableCellElement} th
     * @param {Number} direction
     */
    updateRowHeader: function(i, th, direction) {},

    /**
     * callback for when a table column header element needs updated
     * @type {Function}
     * @param {Number} i
     * @param {HTMLTableCellElement} th
     * @param {HTMLTableColElement} col
     * @param {Number} direction
     */
    updateColumnHeader: function(i, th, col, direction) {},

    useRowHeaders: true,
    useColumnHeaders: true
  };

  MegaTable.left = 0;
  MegaTable.right = 1;
  MegaTable.up = 2;
  MegaTable.down = 3;

  return MegaTable;
})(document);