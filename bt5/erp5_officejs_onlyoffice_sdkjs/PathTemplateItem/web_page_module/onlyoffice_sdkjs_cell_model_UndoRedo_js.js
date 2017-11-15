/*
 * (c) Copyright Ascensio System SIA 2010-2017
 *
 * This program is a free software product. You can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License (AGPL)
 * version 3 as published by the Free Software Foundation. In accordance with
 * Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect
 * that Ascensio System SIA expressly excludes the warranty of non-infringement
 * of any third-party rights.
 *
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For
 * details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html
 *
 * You can contact Ascensio System SIA at Lubanas st. 125a-25, Riga, Latvia,
 * EU, LV-1021.
 *
 * The  interactive user interfaces in modified source and object code versions
 * of the Program must display Appropriate Legal Notices, as required under
 * Section 5 of the GNU AGPL version 3.
 *
 * Pursuant to Section 7(b) of the License you must retain the original Product
 * logo when distributing the program. Pursuant to Section 7(e) we decline to
 * grant you any rights under trademark law for use of our trademarks.
 *
 * All the Product's GUI elements, including illustrations and icon sets, as
 * well as technical writing content are licensed under the terms of the
 * Creative Commons Attribution-ShareAlike 4.0 International. See the License
 * terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode
 *
 */

"use strict";
(
/**
* @param {Window} window
* @param {undefined} undefined
*/
function (window, undefined) {

// Import
var c_oAscLockTypeElem = AscCommonExcel.c_oAscLockTypeElem;
var c_oAscInsertOptions = Asc.c_oAscInsertOptions;
var c_oAscDeleteOptions = Asc.c_oAscDeleteOptions;
	
var gc_nMaxRow0 = AscCommon.gc_nMaxRow0;
var gc_nMaxCol0 = AscCommon.gc_nMaxCol0;
var CellAddress = AscCommon.CellAddress;

var c_oUndoRedoSerializeType =
{
    Null:0,
	Undefined:1,
	SByte:2,
	Byte:3,
	Bool:4,
	Long:5,
	ULong:6,
	Double:7,
	String:8,
	Object:9,
	Array:10
};

function DrawingCollaborativeData()
{
    this.oClass = null;
    this.oBinaryReader = null;
    this.nPos = null;
    this.sChangedObjectId = null;
    this.isDrawingCollaborativeData = true;
}
//главный обьект для пересылки изменений
function UndoRedoItemSerializable(oClass, nActionType, nSheetId, oRange, oData, LocalChange)
{
	this.oClass = oClass;
	this.nActionType = nActionType;
	this.nSheetId = nSheetId;
	this.oRange = oRange;
	this.oData = oData;
	this.LocalChange = LocalChange;
}
UndoRedoItemSerializable.prototype = {
	Serialize : function(oBinaryWriter, collaborativeEditing)
	{
		if((this.oData && this.oData.getType) || this.oClass.Save_Changes || this.oClass.WriteToBinary)
		{
			var oThis = this;
			var oBinaryCommonWriter = new AscCommon.BinaryCommonWriter(oBinaryWriter);
			oBinaryCommonWriter.WriteItemWithLength(function(){oThis.SerializeInner(oBinaryWriter, collaborativeEditing);});
		}
	},
	SerializeInner : function(oBinaryWriter, collaborativeEditing)
	{
		//nClassType
        if(!this.oClass.WriteToBinary)
        {
            oBinaryWriter.WriteBool(true);
            var nClassType = this.oClass.getClassType();
            oBinaryWriter.WriteByte(nClassType);
            //nActionType
            oBinaryWriter.WriteByte(this.nActionType);
            //nSheetId
            if(null != this.nSheetId)
            {
                oBinaryWriter.WriteBool(true);
                oBinaryWriter.WriteString2(this.nSheetId.toString());
            }
            else
                oBinaryWriter.WriteBool(false);
            //oRange
            if(null != this.oRange)
            {
                oBinaryWriter.WriteBool(true);
                var c1 = this.oRange.c1;
                var c2 = this.oRange.c2;
                var r1 = this.oRange.r1;
                var r2 = this.oRange.r2;
                if(null != this.nSheetId && (0 != c1 || gc_nMaxCol0 != c2))
                {
                    c1 = collaborativeEditing.getLockMeColumn2(this.nSheetId, c1);
                    c2 = collaborativeEditing.getLockMeColumn2(this.nSheetId, c2);
                }
                if(null != this.nSheetId && (0 != r1 || gc_nMaxRow0 != r2))
                {
                    r1 = collaborativeEditing.getLockMeRow2(this.nSheetId, r1);
                    r2 = collaborativeEditing.getLockMeRow2(this.nSheetId, r2);
                }
                oBinaryWriter.WriteLong(c1);
                oBinaryWriter.WriteLong(r1);
                oBinaryWriter.WriteLong(c2);
                oBinaryWriter.WriteLong(r2);
            }
            else
                oBinaryWriter.WriteBool(false);
            //oData
            this.SerializeDataObject(oBinaryWriter, this.oData, this.nSheetId, collaborativeEditing);

        }
        else
        {
            oBinaryWriter.WriteBool(false);
            var Class;
			Class = this.oClass.GetClass();
			oBinaryWriter.WriteString2(Class.Get_Id());
			oBinaryWriter.WriteLong(this.oClass.Type);
			this.oClass.WriteToBinary(oBinaryWriter);
        }
	},
	SerializeDataObject : function(oBinaryWriter, oData, nSheetId, collaborativeEditing)
	{
		var oThis = this;
		if(oData.getType)
		{
			var nDataType = oData.getType();
			//не далаем копию oData, а сдвигаем в ней, потому что все равно после сериализации изменения потруться
			if(null != oData.applyCollaborative)
				oData.applyCollaborative(nSheetId, collaborativeEditing);
			oBinaryWriter.WriteByte(nDataType);
			var oBinaryCommonWriter = new AscCommon.BinaryCommonWriter(oBinaryWriter);
			if(oData.Write_ToBinary2)
				oBinaryCommonWriter.WriteItemWithLength(function(){oData.Write_ToBinary2(oBinaryWriter)});
			else
				oBinaryCommonWriter.WriteItemWithLength(function(){oThis.SerializeDataInnerObject(oBinaryWriter, oData, nSheetId, collaborativeEditing);});
		}
		else
		{
			oBinaryWriter.WriteByte(UndoRedoDataTypes.Unknown);
			oBinaryWriter.WriteLong(0);
		}
	},
	SerializeDataInnerObject: function(oBinaryWriter, oData, nSheetId, collaborativeEditing) {
		var oProperties = oData.getProperties();
		for (var i in oProperties) {
			var nItemType = oProperties[i];
			var oItem = oData.getProperty(nItemType);
			this.SerializeDataInner(oBinaryWriter, nItemType, oItem, nSheetId, collaborativeEditing);
		}
	},
	SerializeDataInnerArray: function(oBinaryWriter, oData, nSheetId, collaborativeEditing) {
		for (var i = 0; i < oData.length; ++i) {
			this.SerializeDataInner(oBinaryWriter, 0, oData[i], nSheetId, collaborativeEditing);
		}
	},
	SerializeDataInner: function(oBinaryWriter, nItemType, oItem, nSheetId, collaborativeEditing) {
		var oThis = this;
		var sTypeOf;
		if(null === oItem)
			sTypeOf = "null";
		else if(oItem instanceof Array)
			sTypeOf = "array";
		else
			sTypeOf = typeof(oItem);
		switch(sTypeOf)
		{
			case "object":
				oBinaryWriter.WriteByte(nItemType);
				oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Object);
				this.SerializeDataObject(oBinaryWriter, oItem, nSheetId, collaborativeEditing);
			break;
			case "array":
				oBinaryWriter.WriteByte(nItemType);
				oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Array);
				var oBinaryCommonWriter = new AscCommon.BinaryCommonWriter(oBinaryWriter);
				oBinaryCommonWriter.WriteItemWithLength(function(){oThis.SerializeDataInnerArray(oBinaryWriter, oItem, nSheetId, collaborativeEditing);});
			break;
			case "number":
				oBinaryWriter.WriteByte(nItemType);
				var nFlorItem = Math.floor(oItem);
				if(nFlorItem == oItem)
				{
					if (-128 <= oItem && oItem <= 127) {
						oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.SByte);
						oBinaryWriter.WriteSByte(oItem);
					}
					else if (127 < oItem && oItem <= 255) {
						oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Byte);
						oBinaryWriter.WriteByte(oItem);
					}
					else if (-0x80000000 <= oItem && oItem <= 0x7FFFFFFF) {
						oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Long);
						oBinaryWriter.WriteLong(oItem);
					}
					else if (0x7FFFFFFF < oItem && oItem <= 0xFFFFFFFF) {
						oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.ULong);
						oBinaryWriter.WriteLong(oItem);
					}
					else {
						oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Double);
						oBinaryWriter.WriteDouble2(oItem);
					}
				}
				else
				{
					oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Double);
					oBinaryWriter.WriteDouble2(oItem);
				}
			break;
			case "boolean":
				oBinaryWriter.WriteByte(nItemType);
				oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Bool);
				oBinaryWriter.WriteBool(oItem);
			break;
			case "string":
				oBinaryWriter.WriteByte(nItemType);
				oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.String);
				oBinaryWriter.WriteString2(oItem);
			break;
			case "null":
				oBinaryWriter.WriteByte(nItemType);
				oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Null);
				break;
			case "undefined":
				oBinaryWriter.WriteByte(nItemType);
				oBinaryWriter.WriteByte(c_oUndoRedoSerializeType.Undefined);
				break;
			default:
				break;
		}
	},


	Deserialize : function(oBinaryReader)
	{
		var res = AscCommon.c_oSerConstants.ReadOk;
		res = oBinaryReader.EnterFrame(4);
		var nLength = oBinaryReader.GetULongLE();
		res = oBinaryReader.EnterFrame(nLength);
        if(AscCommon.c_oSerConstants.ReadOk != res)
            return res;
        var bNoDrawing = oBinaryReader.GetBool();
        if(bNoDrawing)
        {
            var nClassType = oBinaryReader.GetUChar();
            this.oClass = UndoRedoClassTypes.Create(nClassType);
            this.nActionType = oBinaryReader.GetUChar();
            var bSheetId = oBinaryReader.GetBool();
            if(bSheetId)
                this.nSheetId = oBinaryReader.GetString2LE(oBinaryReader.GetULongLE());
            var bRange = oBinaryReader.GetBool();
            if(bRange)
            {
                var nC1 = oBinaryReader.GetULongLE();
                var nR1 = oBinaryReader.GetULongLE();
                var nC2 = oBinaryReader.GetULongLE();
                var nR2 = oBinaryReader.GetULongLE();
                this.oRange = new Asc.Range(nC1, nR1, nC2, nR2);
            }
            else
                this.oRange = null;
            this.oData = this.DeserializeData(oBinaryReader);
        }
        else
        {
            var changedObjectId = oBinaryReader.GetString2();
            this.nActionType = 1;
            this.oData = new DrawingCollaborativeData();
            this.oData.sChangedObjectId = changedObjectId;
            this.oData.oBinaryReader = oBinaryReader;
            this.oData.nPos = oBinaryReader.cur;

        }
	},
	DeserializeData : function(oBinaryReader)
	{
		var nDataClassType = oBinaryReader.GetUChar();
		var nLength = oBinaryReader.GetULongLE();
		var oDataObject = UndoRedoDataTypes.Create(nDataClassType);
		if(null != oDataObject)
		{
			if(null != oDataObject.Read_FromBinary2)
				oDataObject.Read_FromBinary2(oBinaryReader);
			else if(null != oDataObject.Read_FromBinary2AndReplace)
				oDataObject = oDataObject.Read_FromBinary2AndReplace(oBinaryReader);
			else
				this.DeserializeDataInner(oBinaryReader, oDataObject, nLength, false);
		}
		else
			oBinaryReader.Skip(nLength);
		return oDataObject;
	},
	DeserializeDataInner : function(oBinaryReader, oDataObject, nLength, bIsArray)
	{
		var nStartPos = oBinaryReader.GetCurPos();
		var nCurPos = nStartPos;
		while(nCurPos - nStartPos < nLength && nCurPos < oBinaryReader.GetSize() - 1)
		{
			var nMemeberType = oBinaryReader.GetUChar();
			var nDataType = oBinaryReader.GetUChar();
			var nUnknownType = false;
			var oNewValue = null;
			switch(nDataType)
			{
				case c_oUndoRedoSerializeType.Null:
					oNewValue = null;
					break;
				case c_oUndoRedoSerializeType.Undefined:
					oNewValue = undefined;
					break;
				case c_oUndoRedoSerializeType.Bool:
					oNewValue = oBinaryReader.GetBool();
					break;
				case c_oUndoRedoSerializeType.SByte:
					oNewValue = oBinaryReader.GetChar();
					break;
				case c_oUndoRedoSerializeType.Byte:
					oNewValue = oBinaryReader.GetUChar();
					break;
				case c_oUndoRedoSerializeType.Long:
					oNewValue = oBinaryReader.GetLongLE();
					break;
				case c_oUndoRedoSerializeType.ULong:
					oNewValue = AscFonts.FT_Common.IntToUInt(oBinaryReader.GetULongLE());
					break;
				case c_oUndoRedoSerializeType.Double:
					oNewValue = oBinaryReader.GetDoubleLE();
					break;
				case c_oUndoRedoSerializeType.String:
					oNewValue = oBinaryReader.GetString2LE(oBinaryReader.GetULongLE());
					break;
				case c_oUndoRedoSerializeType.Object:
					oNewValue = this.DeserializeData(oBinaryReader);
					break;
				case c_oUndoRedoSerializeType.Array:
					var aNewArray = [];
					var nNewLength = oBinaryReader.GetULongLE();
					this.DeserializeDataInner(oBinaryReader, aNewArray, nNewLength, true);
					oNewValue = aNewArray;
					break;
				default:
					nUnknownType = true;
					break;
			}
			if(false == nUnknownType)
			{
				if(bIsArray)
					oDataObject.push(oNewValue);
				else
					oDataObject.setProperty(nMemeberType, oNewValue);
			}
			nCurPos = oBinaryReader.GetCurPos();
		}
	}
};

//для сохранения в историю и пересылки изменений
var UndoRedoDataTypes = new function() {
	this.Unknown = -1;
	this.CellSimpleData = 0;
	this.CellValue = 1;
	this.ValueMultiTextElem = 2;
	this.CellValueData = 3;
	this.CellData = 4;
	this.FromTo = 5;
	this.FromToRowCol = 6;
	this.FromToHyperlink = 7;
	this.IndexSimpleProp = 8;
	this.ColProp = 9;
	this.RowProp = 10;
	this.BBox = 11;
	this.StyleFont = 12;
	this.StyleFill = 13;
	this.StyleNum = 14;
	this.StyleBorder = 15;
	this.StyleBorderProp = 16;
	this.StyleXfs = 17;
	this.StyleAlign = 18;
	this.Hyperlink = 19;
	this.SortData = 20;
	this.CommentData = 21;
	this.CompositeCommentData = 22;
	this.ChartSeriesData = 24;
	this.SheetAdd = 25;
	this.SheetRemove = 26;
	this.ClrScheme = 28;
	this.AutoFilter = 29;
	this.AutoFiltersOptions = 30;
	this.AutoFilterObj = 31;

	this.AutoFiltersOptionsElements = 32;
	this.SingleProperty = 33;
	this.RgbColor = 34;
	this.ThemeColor = 35;
	
	this.CustomFilters = 36;
	this.CustomFilter = 37;
    this.ColorFilter = 38;

    this.DefinedName = 39;
	
	this.AdvancedTableInfoSettings = 40;

    this.GlobalTableIdAdd = 44;
    this.GraphicObjects = 45;
    this.GOPairProps = 46;
    this.GOSingleProp = 47;
    this.GOShapeRecalcTransform = 48;
    this.GOAddAdjustment = 49;
    this.GOAddGuide = 50;
    this.GOAddCnx = 51;
    this.GOHandleXY = 52;
    this.GOHandlePolar = 53;
    this.GOAddPathCommand = 54;
    this.GOAddObject = 55;
    this.GOAddGeometryRect = 56;
    this.GOPathLineToMoveTo = 57;
    this.GOPathArcTo = 58;
    this.GOPathQuadBezTo = 59;
    this.GOPathCubicBezTo = 60;
    this.GOPathClose = 61;
    this.GOSetAdjustmentValue = 62;
	this.AddFormatTableOptions = 63;
  	this.DocContentAddItem = 64;
    this.DocContentRemoveItems = 65;
    this.DocContentParaItemId = 66;
    this.ParagraphAddParaItem = 67;
    this.ParagraphParaItemAdd = 68;
	this.SheetPr = 69;

    this.DynamicFilter = 75;
    this.Top10 = 76;

	this.PropertyChanges = 79;
	this.SparklineProps = 80;

    this.Create = function(nType)
	{
		switch(nType)
		{
			case this.ValueMultiTextElem: return new AscCommonExcel.CCellValueMultiText();break;
			case this.CellValue:return new AscCommonExcel.CCellValue();break;
			case this.CellValueData: return new UndoRedoData_CellValueData();break;
			case this.CellData: return new UndoRedoData_CellData();break;
			case this.CellSimpleData: return new UndoRedoData_CellSimpleData();break;
			case this.FromTo: return new UndoRedoData_FromTo();break;
			case this.FromToRowCol: return new UndoRedoData_FromToRowCol();break;
			case this.FromToHyperlink: return new UndoRedoData_FromToHyperlink();break;
			case this.IndexSimpleProp: return new UndoRedoData_IndexSimpleProp();break;
			case this.ColProp: return new UndoRedoData_ColProp();break;
			case this.RowProp: return new UndoRedoData_RowProp();break;
			case this.BBox: return new UndoRedoData_BBox();break;
			case this.Hyperlink: return new AscCommonExcel.Hyperlink();break;
			case this.SortData: return new UndoRedoData_SortData();break;
			case this.StyleFont: return new AscCommonExcel.Font();break;
			case this.StyleFill: return new AscCommonExcel.Fill();break;
			case this.StyleNum: return new AscCommonExcel.Num();break;
			case this.StyleBorder: return new AscCommonExcel.Border();break;
			case this.StyleBorderProp: return new AscCommonExcel.BorderProp();break;
			case this.StyleXfs: return new AscCommonExcel.CellXfs();break;
			case this.StyleAlign: return new AscCommonExcel.Align();break;
			case this.CommentData: return new Asc.asc_CCommentData();break;
			case this.CompositeCommentData: return new AscCommonExcel.CompositeCommentData();break;
			case this.ChartSeriesData: return new AscFormat.asc_CChartSeria();break;
			case this.SheetAdd: return new UndoRedoData_SheetAdd();break;
			case this.SheetRemove: return new UndoRedoData_SheetRemove();break;
			case this.ClrScheme: return new UndoRedoData_ClrScheme();break;
			case this.AutoFilter: return new UndoRedoData_AutoFilter(); break;
			case this.AutoFiltersOptions: return new Asc.AutoFiltersOptions(); break;
			case this.AutoFilterObj: return new Asc.AutoFilterObj(); break;
			case this.AdvancedTableInfoSettings: return new Asc.AdvancedTableInfoSettings(); break;
			case this.CustomFilters: return new Asc.CustomFilters(); break;
			case this.CustomFilter: return new Asc.CustomFilter(); break;
            case this.ColorFilter: return new Asc.ColorFilter(); break;
            case this.DynamicFilter: return new Asc.DynamicFilter(); break;
            case this.Top10: return new Asc.Top10(); break;
			case this.AutoFiltersOptionsElements: return new AscCommonExcel.AutoFiltersOptionsElements(); break;
			case this.AddFormatTableOptions: return new AscCommonExcel.AddFormatTableOptions(); break;
			case this.SingleProperty: return new UndoRedoData_SingleProperty(); break;
			case this.RgbColor: return new AscCommonExcel.RgbColor(); break;
			case this.ThemeColor: return new AscCommonExcel.ThemeColor(); break;
            case this.GraphicObjects: return new UndoRedoDataGraphicObjects();break;
            case this.GlobalTableIdAdd: return new UndoRedoData_GTableIdAdd(); break;

            case this.GOPairProps: return new UndoRedoDataGOPairProps(); break;
            case this.GOSingleProp: return new UndoRedoDataGOSingleProp(); break;
            case this.GOShapeRecalcTransform: return new UndoRedoDataShapeRecalc(); break;
            case this.GOAddAdjustment: return new UndoRedoDataAddAdjustment(); break;
            case this.GOAddGuide: return new UndoRedoDataAddGuide(); break;
            case this.GOAddCnx: return new UndoRedoDataAddCnx(); break;
            case this.GOHandleXY: return new UndoRedoDataAddHandleXY(); break;
            case this.GOHandlePolar: return new UndoRedoDataAddHandlePolar(); break;
            case this.GOAddPathCommand: return new UndoRedoDataAddPathCommand(); break;
            case this.GOAddObject: return new UndoRedoDataAddObject(); break;
            case this.GOAddGeometryRect: return new UndoRedoDataAddGeometryRect(); break;
            case this.GOPathLineToMoveTo: return new UndoRedoDataMoveToLineTo();break;
            case this.GOPathArcTo: return new UndoRedoDataArcTo(); break;
            case this.GOPathQuadBezTo: return new UndoRedoDataQuadBezTo(); break;
            case this.GOPathCubicBezTo: return new UndoRedoDataCubicBezTo(); break;
            case this.GOPathClose: return new UndoRedoDataClosePath(); break;
            case this.GOSetAdjustmentValue: return new UndoRedoDataSetAdjustmentValue();
            case this.ParagraphAddParaItem: return new UndoRedoDataAddParaItem();
            case this.ParagraphParaItemAdd: return new UndoRedoData_historyitem_Paragraph_AddItem();

            case this.DefinedName: return new UndoRedoData_DefinedNames();
        }
		return null;
	};
};
var g_oUndoRedoData_CellSimpleDataProperties = {
		Row: 0,
		Col: 1,
		NewVal: 2
	};
function UndoRedoData_CellSimpleData(nRow, nCol, oOldVal, oNewVal, sFormula){
	this.Properties = g_oUndoRedoData_CellSimpleDataProperties;
	this.nRow = nRow;
	this.nCol = nCol;
	this.oOldVal = oOldVal;
	this.oNewVal = oNewVal;
	this.sFormula = sFormula;
}
UndoRedoData_CellSimpleData.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.CellSimpleData;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.Row: return this.nRow;break;
			case this.Properties.Col: return this.nCol;break;
			case this.Properties.NewVal: return this.oNewVal;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.Row: this.nRow = value;break;
			case this.Properties.Col: this.nCol = value;break;
			case this.Properties.NewVal: this.oNewVal = value;break;
		}
	},
	applyCollaborative : function(nSheetId, collaborativeEditing)
	{
		this.nRow = collaborativeEditing.getLockMeRow2(nSheetId, this.nRow);
		this.nCol = collaborativeEditing.getLockMeColumn2(nSheetId, this.nCol);
	}
};
var g_oUndoRedoData_CellDataProperties = {
		value: 0,
		style: 1
	};
function UndoRedoData_CellData(value, style){
	this.Properties = g_oUndoRedoData_CellDataProperties;
	this.value = value;
	this.style = style;
}
UndoRedoData_CellData.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.CellData;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.value: return this.value;break;
			case this.Properties.style: return this.style;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.value: this.value = value;break;
			case this.Properties.style: this.style = value;break;
		}
	}
};
var g_oUndoRedoData_CellValueDataProperties = {
		formula: 0,
		value: 1
	};
function UndoRedoData_CellValueData(sFormula, oValue){
	this.Properties = g_oUndoRedoData_CellValueDataProperties;
	this.formula = sFormula;
	this.value = oValue;
}
UndoRedoData_CellValueData.prototype = {
	isEqual : function(val)
	{
		if(null == val)
			return false;
		if(this.formula != val.formula)
			return false;
		if(this.value.isEqual(val.value))
			return true;
		return false;
	},
	getType : function()
	{
		return UndoRedoDataTypes.CellValueData;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.formula: return this.formula;break;
			case this.Properties.value: return this.value;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.formula: this.formula = value;break;
			case this.Properties.value: this.value = value;break;
		}
	}
};
var g_oUndoRedoData_FromToRowColProperties = {
		from: 0,
		to: 1,
        bRow: 2
	};
function UndoRedoData_FromToRowCol(bRow, from, to){
	this.Properties = g_oUndoRedoData_FromToRowColProperties;
	this.bRow = bRow;
	this.from = from;
	this.to = to;
}
UndoRedoData_FromToRowCol.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.FromToRowCol;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.from: return this.from;break;
			case this.Properties.to: return this.to;break;
            case this.Properties.bRow: return this.bRow;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.from: this.from = value;break;
			case this.Properties.to: this.to = value;break;
            case this.Properties.bRow: this.bRow = value;break;
		}
	},
	applyCollaborative : function(nSheetId, collaborativeEditing)
	{
		if(this.bRow)
		{
			this.from = collaborativeEditing.getLockMeRow2(nSheetId, this.from);
			this.to = collaborativeEditing.getLockMeRow2(nSheetId, this.to);
		}
		else
		{
			this.from = collaborativeEditing.getLockMeColumn2(nSheetId, this.from);
			this.to = collaborativeEditing.getLockMeColumn2(nSheetId, this.to);
		}
	}
};
var g_oUndoRedoData_FromToProperties = {
		from: 0,
		to: 1,
        copyRange: 2
	};
function UndoRedoData_FromTo(from, to, copyRange){
	this.Properties = g_oUndoRedoData_FromToProperties;
	this.from = from;
	this.to = to;
    this.copyRange = copyRange;
}
UndoRedoData_FromTo.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.FromTo;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.from: return this.from;break;
			case this.Properties.to: return this.to;break;
			case this.Properties.copyRange: return this.copyRange;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.from: this.from = value;break;
			case this.Properties.to: this.to = value;break;
			case this.Properties.copyRange: this.copyRange = value;break;
		}
	}
};
var g_oUndoRedoData_FromToHyperlinkProperties = {
		from: 0,
		to: 1,
		hyperlink: 2
	};
function UndoRedoData_FromToHyperlink(oBBoxFrom, oBBoxTo, hyperlink){
	this.Properties = g_oUndoRedoData_FromToHyperlinkProperties;
	this.from = new UndoRedoData_BBox(oBBoxFrom);
	this.to = new UndoRedoData_BBox(oBBoxTo);
	this.hyperlink = hyperlink;
}
UndoRedoData_FromToHyperlink.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.FromToHyperlink;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.from: return this.from;break;
			case this.Properties.to: return this.to;break;
			case this.Properties.hyperlink: return this.hyperlink;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.from: this.from = value;break;
			case this.Properties.to: this.to = value;break;
			case this.Properties.hyperlink: this.hyperlink = value;break;
		}
	},
	applyCollaborative : function(nSheetId, collaborativeEditing)
	{
		this.from.r1 = collaborativeEditing.getLockMeRow2(nSheetId, this.from.r1);
		this.from.r2 = collaborativeEditing.getLockMeRow2(nSheetId, this.from.r2);
		this.from.c1 = collaborativeEditing.getLockMeColumn2(nSheetId, this.from.c1);
		this.from.c2 = collaborativeEditing.getLockMeColumn2(nSheetId, this.from.c2);

		this.to.r1 = collaborativeEditing.getLockMeRow2(nSheetId, this.to.r1);
		this.to.r2 = collaborativeEditing.getLockMeRow2(nSheetId, this.to.r2);
		this.to.c1 = collaborativeEditing.getLockMeColumn2(nSheetId, this.to.c1);
		this.to.c2 = collaborativeEditing.getLockMeColumn2(nSheetId, this.to.c2);
	}
};
var g_oUndoRedoData_IndexSimplePropProperties = {
		index: 0,
		oNewVal: 1
	};
function UndoRedoData_IndexSimpleProp(index, bRow, oOldVal, oNewVal){
	this.Properties = g_oUndoRedoData_IndexSimplePropProperties;
	this.index = index;
	this.bRow = bRow;
	this.oOldVal = oOldVal;
	this.oNewVal = oNewVal;
}
UndoRedoData_IndexSimpleProp.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.IndexSimpleProp;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.index: return this.index;break;
			case this.Properties.oNewVal: return this.oNewVal;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.index: this.index = value;break;
			case this.Properties.oNewVal: this.oNewVal = value;break;
		}
	},
	applyCollaborative : function(nSheetId, collaborativeEditing)
	{
		if(this.bRow)
			this.index = collaborativeEditing.getLockMeRow2(nSheetId, this.index);
		else
			this.index = collaborativeEditing.getLockMeColumn2(nSheetId, this.index);
	}
};
var g_oUndoRedoData_ColPropProperties = {
		width: 0,
		hd: 1,
		CustomWidth: 2,
		BestFit: 3
	};
function UndoRedoData_ColProp(col){
	this.Properties = g_oUndoRedoData_ColPropProperties;
	if(null != col)
	{
		this.width = col.width;
		this.hd = col.hd;
		this.CustomWidth = col.CustomWidth;
		this.BestFit = col.BestFit;
	}
	else
	{
		this.width = null;
		this.hd = null;
		this.CustomWidth = null;
		this.BestFit = null;
	}
}
UndoRedoData_ColProp.prototype = {
	isEqual : function(val)
	{
		var defaultColWidth = AscCommonExcel.oDefaultMetrics.ColWidthChars;
		return this.hd == val.hd && this.CustomWidth == val.CustomWidth && ((this.BestFit == val.BestFit && this.width == val.width) ||
			((null == this.width || defaultColWidth == this.width) && (null == this.BestFit || true == this.BestFit) &&
			(null == val.width || defaultColWidth == val.width) && (null == val.BestFit || true == val.BestFit)));
	},
	getType : function()
	{
		return UndoRedoDataTypes.ColProp;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.width: return this.width;break;
			case this.Properties.hd: return this.hd;break;
			case this.Properties.CustomWidth: return this.CustomWidth;break;
			case this.Properties.BestFit: return this.BestFit;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.width: this.width = value;break;
			case this.Properties.hd: this.hd = value;break;
			case this.Properties.CustomWidth: this.CustomWidth = value;break;
			case this.Properties.BestFit: this.BestFit = value;break;
		}
	}
};
var g_oUndoRedoData_RowPropProperties = {
		h: 0,
		hd: 1,
		CustomHeight: 2
	};
function UndoRedoData_RowProp(row){
	this.Properties = g_oUndoRedoData_RowPropProperties;
	if(null != row)
	{
		this.h = row.h;
		this.hd = row.getHidden();
		this.CustomHeight = row.getCustomHeight();
	}
	else
	{
		this.h = null;
		this.hd = null;
		this.CustomHeight = null;
	}
}
UndoRedoData_RowProp.prototype = {
	isEqual : function(val)
	{
		var defaultRowHeight = AscCommonExcel.oDefaultMetrics.RowHeight;
		return this.hd == val.hd && ((this.CustomHeight == val.CustomHeight && this.h == val.h) ||
			((null == this.h || defaultRowHeight == this.h) && (null == this.CustomHeight || false == this.CustomHeight) &&
			(null == val.h || defaultRowHeight == val.h) && (null == val.CustomHeight || false == val.CustomHeight)));
	},
	getType : function()
	{
		return UndoRedoDataTypes.RowProp;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.h: return this.h;break;
			case this.Properties.hd: return this.hd;break;
			case this.Properties.CustomHeight: return this.CustomHeight;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.h: this.h = value;break;
			case this.Properties.hd: this.hd = value;break;
			case this.Properties.CustomHeight: this.CustomHeight = value;break;
		}
	}
};
var g_oUndoRedoData_BBoxProperties = {
		c1: 0,
		r1: 1,
		c2: 2,
		r2: 3
	};
function UndoRedoData_BBox(oBBox){
	this.Properties = g_oUndoRedoData_BBoxProperties;
	if(null != oBBox)
	{
		this.c1 = oBBox.c1;
		this.r1 = oBBox.r1;
		this.c2 = oBBox.c2;
		this.r2 = oBBox.r2;
	}
	else
	{
		this.c1 = null;
		this.r1 = null;
		this.c2 = null;
		this.r2 = null;
	}
}
UndoRedoData_BBox.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.BBox;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.c1: return this.c1;break;
			case this.Properties.r1: return this.r1;break;
			case this.Properties.c2: return this.c2;break;
			case this.Properties.r2: return this.r2;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.c1: this.c1 = value;break;
			case this.Properties.r1: this.r1 = value;break;
			case this.Properties.c2: this.c2 = value;break;
			case this.Properties.r2: this.r2 = value;break;
		}
	},
	applyCollaborative : function(nSheetId, collaborativeEditing)
	{
		this.r1 = collaborativeEditing.getLockMeRow2(nSheetId, this.r1);
		this.r2 = collaborativeEditing.getLockMeRow2(nSheetId, this.r2);
		this.c1 = collaborativeEditing.getLockMeColumn2(nSheetId, this.c1);
		this.c2 = collaborativeEditing.getLockMeColumn2(nSheetId, this.c2);
	}
};
var g_oUndoRedoData_SortDataProperties = {
		bbox: 0,
		places: 1
	};
function UndoRedoData_SortData(bbox, places){
	this.Properties = g_oUndoRedoData_SortDataProperties;
	this.bbox = bbox;
	this.places = places;
}
UndoRedoData_SortData.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.SortData;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.bbox: return this.bbox;break;
			case this.Properties.places: return this.places;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.bbox: this.bbox = value;break;
			case this.Properties.places: this.places = value;break;
		}
	},
	applyCollaborative : function(nSheetId, collaborativeEditing)
	{
		this.bbox.r1 = collaborativeEditing.getLockMeRow2(nSheetId, this.bbox.r1);
		this.bbox.r2 = collaborativeEditing.getLockMeRow2(nSheetId, this.bbox.r2);
		this.bbox.c1 = collaborativeEditing.getLockMeColumn2(nSheetId, this.bbox.c1);
		this.bbox.c2 = collaborativeEditing.getLockMeColumn2(nSheetId, this.bbox.c2);
		for(var i = 0, length = this.places.length; i < length; ++i)
		{
			var place = this.places[i];
			place.from = collaborativeEditing.getLockMeRow2(nSheetId, place.from);
			place.to = collaborativeEditing.getLockMeRow2(nSheetId, place.to);
		}
	}
};


function UndoRedoData_GTableIdAdd(object, id)
{
    this.Properties =
    {
        objectType: 0,
        id: 1
    };

    if( AscCommon.isRealObject(object) && typeof object.getObjectType === "function" )
    this.objectType = object.getObjectType();
    this.id = id;
}
UndoRedoData_GTableIdAdd.prototype =
{
    getType: function()
    {
        return UndoRedoDataTypes.GlobalTableIdAdd;
    },

    getProperties: function()
    {
        return this.Properties;
    },

    getProperty: function(nType)
    {
        switch(nType)
        {
            case this.Properties.objectType: return this.objectType;
            case this.Properties.id: return this.id;
        }
		return null;
    },

    setProperty: function(nType, value)
    {
        switch (nType)
        {
            case this.Properties.objectType:
            {
                this.objectType = value;
                break;
            }
            case this.Properties.id:
            {
                this.id = value;
                break;
            }
        }
    }
};


function UndoRedoData_historyitem_Paragraph_AddItem(startPos, endPos, itemsIds)
{
    this.Properties =
    {
        startPos: 0,
        endPos: 1,
        itemsIds: 2
    };

    this.startPos = startPos;
    this.endPos = endPos;
    this.itemsIds = itemsIds;
}
UndoRedoData_historyitem_Paragraph_AddItem.prototype =
{
    getType: function()
    {
        return UndoRedoDataTypes.ParagraphParaItemAdd;
    },

    getProperties: function()
    {
        return this.Properties;
    },

    getProperty: function(nType)
    {
        switch (nType)
        {
            case this.Properties.startPos: return this.startPos;
            case this.Properties.endPos: return this.endPos;
            case this.Properties.itemsIds: return this.itemsIds;
        }
		return null;
    },

    setProperty: function(nType, value)
    {
        switch (nType)
        {
            case this.Properties.startPos:
            {
                this.startPos = value;
                break;
            }
            case this.Properties.endPos:
            {
                this.endPos = value;
                break;
            }
            case this.Properties.itemsIds:
            {
                this.itemsIds = value;
            }
        }
    }
};

function UndoRedoDataDocContentAddItem(pos, objectId)
{
    this.Properties =
    {
        pos: 0,
        objectId: 1
    };
    this.pos = pos;
    this.objectId = objectId;
}

UndoRedoDataDocContentAddItem.prototype =
{
    getType: function()
    {
        return UndoRedoDataTypes.DocContentAddItem;
    },

    getProperties: function()
    {
        return this.Properties;
    },

    getProperty: function(nType)
    {
        switch(nType)
        {
            case this.Properties.pos: return this.pos;
            case this.Properties.objectId: return this.objectId;
        }
		return null;
    },

    setProperty: function(nType, value)
    {
        switch (nType)
        {
            case this.Properties.pos:
            {
                this.pos = value;
                break;
            }
            case this.Properties.objectId:
            {
                this.objectId = value;
                break;
            }
        }
    }
};


function UndoRedoDataTypeParaItemId(itemId)
{
    this.Properties =
    {
        itemId: 0
    };
    this.itemId = itemId;
}

UndoRedoDataTypeParaItemId.prototype =
{
    getType: function()
    {
        return UndoRedoDataTypes.DocContentParaItemId;
    },

    getProperties: function()
    {
        return this.Properties;
    },

    getProperty: function(nType)
    {
        switch(nType)
        {
            case this.Properties.itemId: return this.itemId;
        }
		return null;
    },

    setProperty: function(nType, value)
    {
        switch (nType)
        {
            case this.Properties.itemId:
            {
                this.itemId = value;
                break;
            }
        }
    }
};



function UndoRedoDataAddParaItem(type, value)
{
    this.Properties =
    {
        type: 0, value : 1
    };
    this.type = type;
    this.value = value;
}

UndoRedoDataAddParaItem.prototype =
{
    getType: function()
    {
        return UndoRedoDataTypes.ParagraphAddParaItem;
    },

    getProperties: function()
    {
        return this.Properties;
    },

    getProperty: function(nType)
    {
        switch(nType)
        {
            case this.Properties.type: return this.type;
            case this.Properties.value: return this.value;
        }
		return null;
    },

    setProperty: function(nType, value)
    {
        switch (nType)
        {
            case this.Properties.type:
            {
                this.type = value;
                break;
            }
            case this.Properties.value:
            {
                this.value = value;
                break;
            }
        }
    }
};

function UndoRedoDataDocContentRemoveItems(pos, aItems)
{
    this.Properties =
    {
        pos: 0,
        aItems: 1
    };
    this.pos = pos;
    this.aItems = aItems;
}

UndoRedoDataDocContentRemoveItems.prototype =
{
    getType: function()
    {
        return UndoRedoDataTypes.DocContentRemoveItems;
    },

    getProperties: function()
    {
        return this.Properties;
    },

    getProperty: function(nType)
    {
        switch(nType)
        {
            case this.Properties.pos: return this.pos;
            case this.Properties.aItems: return this.aItems;
        }
		return null;
    },

    setProperty: function(nType, value)
    {
        switch (nType)
        {
            case this.Properties.pos:
            {
                this.pos = value;
                break;
            }
            case this.Properties.aItems:
            {
                this.aItems = value;
                break;
            }
        }
    }
};

function UndoRedoDataParaPr(paraPr)
{
    this.Properties =
    {
        ContextualSpacing : 0,
        IndLeft      : 1, // Левый отступ
        IndRight     : 2, // Правый отступ
        IndFirstLine : 3, // Первая строка// Удалять ли интервал между параграфами одинакового стиля
        Jc                : 4,          // Прилегание параграфа
        KeepLines         : 5,          // Неразрывный параграф
        KeepNext          : 6,          // Не разъединять со следующим параграфом
        PageBreakBefore   : 7,          // Разрыв страницы перед параграфом
        SpacingLine              : 8, // Расстояние между строками внутри абзаца
        SpacingLineRule          : 9, // Тип расстрояния между строками
        SpacingBefore            : 10, // Дополнительное расстояние до абзаца
        SpacingBeforeAutoSpacing : 11, // Использовать ли автоматический расчет расстояния до параграфа
        SpacingAfter             : 12, // Дополнительное расстояние после абзаца
        SpacingAfterAutoSpacing  : 13, // Использовать ли автоматический расчет расстояния после параграфа
        Shd               : 14,          // Заливка параграфа
        BrdFirst   : 15,            // Является ли данный параграф первым в группе параграфов с одинаковыми краями и настройками границ
        BrdLast    : 16,            // Является ли данный параграф последним в группе параграфов с одинаковыми краями и настройками границ
        BrdBetween : 17,
        BrdBottom  : 18,
        BrdLeft    : 19,
        BrdRight   : 20,
        BrdTop     : 21,
        WidowControl      : 22, // Запрет висячих строк
        Tabs              : 23, // Заданные табы
        NumPr             : 24, // Нумерация
        PStyle            : 25 // Стиль параграфа
    };

    this.ContextualSpacing = paraPr.ContextualSpacing;
    this.IndLeft      = paraPr.Ind.Left     ; // Левый отступ
    this.IndRight     = paraPr.Ind.Right    ; // Правый отступ
    this.IndFirstLine = paraPr.Ind.FirstLine; // Первая строка// Удалять ли интервал между параграфами одинакового стиля
    this.Jc                = paraPr.Jc;          // Прилегание параграфа
    this.KeepLines         = paraPr.KeepLines;          // Неразрывный параграф
    this.KeepNext          = paraPr.KeepNext;          // Не разъединять со следующим параграфом
    this.PageBreakBefore   = paraPr.PageBreakBefore;          // Разрыв страницы перед параграфом
    this.SpacingLine              = paraPr.Spacing.Line             ; // Расстояние между строками внутри абзаца
    this.SpacingLineRule          = paraPr.Spacing.LineRule         ; // Тип расстрояния между строками
    this.SpacingBefore            = paraPr.Spacing.Before           ; // Дополнительное расстояние до абзаца
    this.SpacingBeforeAutoSpacing = paraPr.Spacing.BeforeAutoSpacing; // Использовать ли автоматический расчет расстояния до параграфа
    this.SpacingAfter             = paraPr.Spacing.After            ; // Дополнительное расстояние после абзаца
    this.SpacingAfterAutoSpacing  = paraPr.Spacing.AfterAutoSpacing ; // Использовать ли автоматический расчет расстояния после параграфа
    this.Shd               = paraPr.Shd;          // Заливка параграфа
    this.BrdFirst   = paraPr.BrdFirst  ;            // Является ли данный параграф первым в группе параграфов с одинаковыми краями и настройками границ
    this.BrdLast    = paraPr.BrdLast   ;            // Является ли данный параграф последним в группе параграфов с одинаковыми краями и настройками границ
    this.BrdBetween = paraPr.BrdBetween;
    this.BrdBottom  = paraPr.BrdBottom ;
    this.BrdLeft    = paraPr.BrdLeft   ;
    this.BrdRight   = paraPr.BrdRight  ;
    this.BrdTop     = paraPr.BrdTop    ;
    this.WidowControl      = paraPr.WidowControl; // Запрет висячих строк
    this.Tabs              = paraPr.Tabs        ; // Заданные табы
    this.NumPr             = paraPr.NumPr       ; // Нумерация
    this.PStyle            = paraPr.PStyle      ;// Стиль параграфа

}

UndoRedoDataParaPr.prototype = {
    getType : function()
    {
        return UndoRedoDataTypes.SheetPositions;
    },
    getProperties : function()
    {
        return this.Properties;
    },
    getProperty : function(nType)
    {
        switch(nType)
        {
               case this.Properties.ContextualSpacing       : return   this.ContextualSpacing       ;
               case this.Properties.IndLeft                 : return   this.IndLeft                 ;
               case this.Properties.IndRight                : return   this.IndRight                ;
               case this.Properties.IndFirstLine            : return   this.IndFirstLine            ;
               case this.Properties.Jc                      : return   this.Jc                      ;
               case this.Properties.KeepLines               : return   this.KeepLines               ;
               case this.Properties.KeepNext                : return   this.KeepNext                ;
               case this.Properties.PageBreakBefore         : return   this.PageBreakBefore         ;
               case this.Properties.SpacingLine             : return   this.SpacingLine             ;
               case this.Properties.SpacingLineRule         : return   this.SpacingLineRule         ;
               case this.Properties.SpacingBefore           : return   this.SpacingBefore           ;
               case this.Properties.SpacingBeforeAutoSpacing: return   this.SpacingBeforeAutoSpacing;
               case this.Properties.SpacingAfter            : return   this.SpacingAfter            ;
               case this.Properties.SpacingAfterAutoSpacing : return   this.SpacingAfterAutoSpacing ;
               case this.Properties.Shd                     : return   this.Shd                     ;
               case this.Properties.BrdFirst                : return   this.BrdFirst                ;
               case this.Properties.BrdLast                 : return   this.BrdLast                 ;
               case this.Properties.BrdBetween              : return   this.BrdBetween              ;
               case this.Properties.BrdBottom               : return   this.BrdBottom               ;
               case this.Properties.BrdLeft                 : return   this.BrdLeft                 ;
               case this.Properties.BrdRight                : return   this.BrdRight                ;
               case this.Properties.BrdTop                  : return   this.BrdTop                  ;
               case this.Properties.WidowControl            : return   this.WidowControl            ;
               case this.Properties.Tabs                    : return   this.Tabs                    ;
               case this.Properties.NumPr                   : return   this.NumPr                   ;
               case this.Properties.PStyle                  : return   this.PStyle                  ;
        }
		return null;
    },
    setProperty : function(nType, value)
    {
        switch(nType)
        {
            case this.Properties.ContextualSpacing       : this.ContextualSpacing        = value; break;
            case this.Properties.IndLeft                 : this.IndLeft                  = value; break;
            case this.Properties.IndRight                : this.IndRight                 = value; break;
            case this.Properties.IndFirstLine            : this.IndFirstLine             = value; break;
            case this.Properties.Jc                      : this.Jc                       = value; break;
            case this.Properties.KeepLines               : this.KeepLines                = value; break;
            case this.Properties.KeepNext                : this.KeepNext                 = value; break;
            case this.Properties.PageBreakBefore         : this.PageBreakBefore          = value; break;
            case this.Properties.SpacingLine             : this.SpacingLine              = value; break;
            case this.Properties.SpacingLineRule         : this.SpacingLineRule          = value; break;
            case this.Properties.SpacingBefore           : this.SpacingBefore            = value; break;
            case this.Properties.SpacingBeforeAutoSpacing: this.SpacingBeforeAutoSpacing = value; break;
            case this.Properties.SpacingAfter            : this.SpacingAfter             = value; break;
            case this.Properties.SpacingAfterAutoSpacing : this.SpacingAfterAutoSpacing  = value; break;
            case this.Properties.Shd                     : this.Shd                      = value; break;
            case this.Properties.BrdFirst                : this.BrdFirst                 = value; break;
            case this.Properties.BrdLast                 : this.BrdLast                  = value; break;
            case this.Properties.BrdBetween              : this.BrdBetween               = value; break;
            case this.Properties.BrdBottom               : this.BrdBottom                = value; break;
            case this.Properties.BrdLeft                 : this.BrdLeft                  = value; break;
            case this.Properties.BrdRight                : this.BrdRight                 = value; break;
            case this.Properties.BrdTop                  : this.BrdTop                   = value; break;
            case this.Properties.WidowControl            : this.WidowControl             = value; break;
            case this.Properties.Tabs                    : this.Tabs                     = value; break;
            case this.Properties.NumPr                   : this.NumPr                    = value; break;
            case this.Properties.PStyle                  : this.PStyle                   = value; break;
        }
    }
};

var g_oUndoRedoData_SheetAddProperties = {
		name: 0,
		sheetidfrom: 1,
		sheetid: 2,
        tableNames: 3,
		insertBefore: 4
	};
function UndoRedoData_SheetAdd(insertBefore, name, sheetidfrom, sheetid, tableNames){
	this.Properties = g_oUndoRedoData_SheetAddProperties;
	this.insertBefore= insertBefore;
	this.name = name;
	this.sheetidfrom = sheetidfrom;
	this.sheetid = sheetid;
	//Эти поля заполняются после Undo/Redo
	this.sheet = null;

    this.tableNames = tableNames;
}
UndoRedoData_SheetAdd.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.SheetAdd;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.name: return this.name;break;
			case this.Properties.sheetidfrom: return this.sheetidfrom;break;
			case this.Properties.sheetid: return this.sheetid;break;
            case this.Properties.tableNames: return this.tableNames;break;
			case this.Properties.insertBefore: return this.insertBefore;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.name: this.name = value;break;
			case this.Properties.sheetidfrom: this.sheetidfrom = value;break;
			case this.Properties.sheetid: this.sheetid = value;break;
            case this.Properties.tableNames: this.tableNames = value;break;
			case this.Properties.insertBefore: this.insertBefore = value;break;
		}
	}
};
var g_oUndoRedoData_SheetRemoveProperties = {
		sheetId: 0,
		sheet: 1
	};
function UndoRedoData_SheetRemove(index, sheetId, sheet){
	this.Properties = g_oUndoRedoData_SheetRemoveProperties;
	this.index = index;
	this.sheetId = sheetId;
	this.sheet = sheet;
}
UndoRedoData_SheetRemove.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.SheetRemove;
	},
	getProperties : function()
	{
		return this.Properties;
	},
	getProperty : function(nType)
	{
		switch(nType)
		{
			case this.Properties.sheetId: return this.sheetId;break;
			case this.Properties.sheet: return this.sheet;break;
		}
		return null;
	},
	setProperty : function(nType, value)
	{
		switch(nType)
		{
			case this.Properties.sheetId: this.sheetId = value;break;
			case this.Properties.sheet: this.sheet = value;break;
		}
	}
};

var g_oUndoRedoData_DefinedNamesProperties = {
    name: 0,
    ref:1,
    sheetId:2,
    isTable:4
};
function UndoRedoData_DefinedNames(name, ref, sheetId, isTable){
    this.Properties = g_oUndoRedoData_DefinedNamesProperties;
    this.name = name;
    this.ref = ref;
    this.sheetId = sheetId;
    this.isTable = isTable;
}
UndoRedoData_DefinedNames.prototype = {
    getType : function()
    {
        return UndoRedoDataTypes.DefinedName;
    },
    getProperties : function()
    {
        return this.Properties;
    },
    getProperty : function(nType)
    {
        switch(nType)
        {
            case this.Properties.name: return this.name;break;
            case this.Properties.ref: return this.ref;break;
            case this.Properties.sheetId: return this.sheetId;break;
            case this.Properties.isTable: return this.isTable;break;
        }
        return null;
    },
    setProperty : function(nType, value)
    {
        switch(nType)
        {
            case this.Properties.name: this.name = value;break;
            case this.Properties.ref: this.ref = value;break;
            case this.Properties.sheetId: this.sheetId = value;break;
            case this.Properties.isTable: this.isTable = value;break;
        }
    }
};

function UndoRedoData_ClrScheme(oldVal, newVal){
	this.oldVal = oldVal;
	this.newVal = newVal;
}
UndoRedoData_ClrScheme.prototype = {
	getType : function()
	{
		return UndoRedoDataTypes.ClrScheme;
	},
	Write_ToBinary2 : function(writer)
	{
		this.newVal.Write_ToBinary(writer);
	},
	Read_FromBinary2 : function(reader)
	{
		this.newVal = new AscFormat.ClrScheme();
		this.newVal.Read_FromBinary(reader);
	}
};
var g_oUndoRedoData_AutoFilterProperties = {
		activeCells			: 0,
		styleName			: 1,
		type				: 2,
		cellId				: 3,
		autoFiltersObject	: 4,
		addFormatTableOptionsObj: 5,
		moveFrom            : 6,
		moveTo              : 7,
		bWithoutFilter      : 8,
		displayName         : 9,
        val                 : 10,
		ShowColumnStripes   : 11,
		ShowFirstColumn     : 12,
		ShowLastColumn      : 13,
		ShowRowStripes      : 14,
		HeaderRowCount      : 15,
		TotalsRowCount      : 16,
		color               : 17,
		tablePart           : 18,
		nCol                : 19,
		nRow                : 20,
		formula             : 21
};
function UndoRedoData_AutoFilter() {
	this.Properties = g_oUndoRedoData_AutoFilterProperties;

	this.undo				= null;

	this.activeCells		= null;
	this.styleName			= null;
	this.type				= null;
	this.cellId				= null;
	this.autoFiltersObject	= null;
	this.addFormatTableOptionsObj = null;
	this.moveFrom           = null;
	this.moveTo             = null;
	this.bWithoutFilter     = null;
	this.displayName        = null;
    this.val                = null;

    this.ShowColumnStripes  = null;
    this.ShowFirstColumn    = null;
    this.ShowLastColumn     = null;
    this.ShowRowStripes     = null;

    this.HeaderRowCount     = null;
    this.TotalsRowCount     = null;
	this.color              = null;
	this.tablePart          = null;
	this.nCol               = null;
	this.nRow               = null;
	this.formula            = null;
}
UndoRedoData_AutoFilter.prototype = {
	getType : function ()
	{
		return UndoRedoDataTypes.AutoFilter;
	},
	getProperties : function ()
	{
		return this.Properties;
	},
	getProperty : function (nType)
	{
		switch (nType)
		{
			case this.Properties.activeCells: return new UndoRedoData_BBox(this.activeCells); break;
			case this.Properties.styleName: return this.styleName; break;
			case this.Properties.type: return this.type; break;
			case this.Properties.cellId: return this.cellId; break;
			case this.Properties.autoFiltersObject: return this.autoFiltersObject; break;
			case this.Properties.addFormatTableOptionsObj: return this.addFormatTableOptionsObj; break;
			case this.Properties.moveFrom: return new UndoRedoData_BBox(this.moveFrom); break;
			case this.Properties.moveTo: return new UndoRedoData_BBox(this.moveTo); break;
			case this.Properties.bWithoutFilter: return this.bWithoutFilter; break;
			case this.Properties.displayName: return this.displayName; break;
            case this.Properties.val: return this.val; break;
            case this.Properties.ShowColumnStripes: return this.ShowColumnStripes; break;
            case this.Properties.ShowFirstColumn: return this.ShowFirstColumn; break;
            case this.Properties.ShowLastColumn: return this.ShowLastColumn; break;
            case this.Properties.ShowRowStripes: return this.ShowRowStripes; break;
            case this.Properties.HeaderRowCount: return this.HeaderRowCount; break;
            case this.Properties.TotalsRowCount: return this.TotalsRowCount; break;
			case this.Properties.color: return this.color; break;
			case this.Properties.tablePart:
			{
				var tablePart = this.tablePart;
				if(tablePart)
				{
					var memory = new AscCommon.CMemory();
					var aDxfs = [];
					var oBinaryTableWriter = new AscCommonExcel.BinaryTableWriter(memory, aDxfs);
					oBinaryTableWriter.WriteTable(tablePart);
					tablePart = memory.GetBase64Memory();
				}

				return tablePart; break;
			}
			case this.Properties.nCol: return this.nCol; break;
			case this.Properties.nRow: return this.nRow; break;
			case this.Properties.formula: return this.formula; break;
		}

		return null;
	},
	setProperty : function (nType, value)
	{
		switch (nType)
		{
			case this.Properties.activeCells: this.activeCells = new Asc.Range(value.c1, value.r1, value.c2, value.r2);break;
			case this.Properties.styleName: this.styleName = value;break;
			case this.Properties.type: this.type = value;break;
			case this.Properties.cellId: this.cellId = value;break;
			case this.Properties.autoFiltersObject: this.autoFiltersObject = value;break;
			case this.Properties.addFormatTableOptionsObj: return this.addFormatTableOptionsObj = value; break;
			case this.Properties.moveFrom: this.moveFrom = value;break;
			case this.Properties.moveTo: this.moveTo = value;break;
			case this.Properties.bWithoutFilter: this.bWithoutFilter = value;break;
			case this.Properties.displayName: this.displayName = value;break;
            case this.Properties.val: this.val = value;break;
            case this.Properties.ShowColumnStripes: this.ShowColumnStripes = value;break;
            case this.Properties.ShowFirstColumn: this.ShowFirstColumn = value;break;
            case this.Properties.ShowLastColumn: this.ShowLastColumn = value;break;
            case this.Properties.ShowRowStripes: this.ShowRowStripes = value;break;
            case this.Properties.HeaderRowCount: this.HeaderRowCount = value;break;
            case this.Properties.TotalsRowCount: this.TotalsRowCount = value;break;
			case this.Properties.color: this.color = value;break;
			case this.Properties.tablePart:
			{
				var table;
				if(value)
				{
					//TODO длину скорее всего нужно записывать
					var dstLen = 0;
					dstLen += value.length;

					var pointer = g_memory.Alloc(dstLen);
					var stream = new AscCommon.FT_Stream2(pointer.data, dstLen);
					stream.obj = pointer.obj;

					var nCurOffset = 0;
					var oBinaryFileReader = new AscCommonExcel.BinaryFileReader();
					nCurOffset = oBinaryFileReader.getbase64DecodedData2(value, 0, stream, nCurOffset);

					var dxfs = [];
					var oBinaryTableReader = new AscCommonExcel.Binary_TableReader(stream, null, null, dxfs);
					oBinaryTableReader.stream = stream;
					oBinaryTableReader.oReadResult = {
						tableCustomFunc: []
					};

					var table = new AscCommonExcel.TablePart();
					var res = oBinaryTableReader.bcr.Read1(dstLen, function(t,l){
						return oBinaryTableReader.ReadTable(t, l, table);
					});
				}

				if(table)
				{
					this.tablePart = table;
				}
				break;
			}
			case this.Properties.nCol: this.nCol = value;break;
			case this.Properties.nRow: this.nRow = value;break;
			case this.Properties.formula: this.formula = value;break;
		}
		return null;
	},
	applyCollaborative : function (nSheetId, collaborativeEditing) {
		this.activeCells.c1 = collaborativeEditing.getLockMeColumn2(nSheetId, this.activeCells.c1);
		this.activeCells.c2 = collaborativeEditing.getLockMeColumn2(nSheetId, this.activeCells.c2);
		this.activeCells.r1 = collaborativeEditing.getLockMeRow2(nSheetId, this.activeCells.r1);
		this.activeCells.r2 = collaborativeEditing.getLockMeRow2(nSheetId, this.activeCells.r2);
	}
};
var g_oUndoRedoData_SinglePropertyProperties = {
		elem : 0
	};
function UndoRedoData_SingleProperty(elem) {
	this.Properties = g_oUndoRedoData_SinglePropertyProperties;
	this.elem = elem;
}
UndoRedoData_SingleProperty.prototype = {
	getType : function ()
	{
		return UndoRedoDataTypes.SingleProperty;
	},
	getProperties : function ()
	{
		return this.Properties;
	},
	getProperty : function (nType)
	{
		switch (nType)
		{
			case this.Properties.elem: return this.elem; break;
		}
		return null;
	},
	setProperty : function (nType, value)
	{
		switch (nType)
		{
			case this.Properties.elem: this.elem = value;break;
		}
	}
};

//для применения изменений
var UndoRedoClassTypes = new function(){
	this.aTypes = [];
	this.Add = function(fCreate)
	{
		var nRes = this.aTypes.length;
		this.aTypes.push(fCreate);
		return nRes;
	};
	this.Create = function(nType)
	{
		if(nType < this.aTypes.length)
			return this.aTypes[nType]();
		return null;
	};
};


function UndoRedoDataGraphicObjects(objectId, drawingData)
{
    this.Properties =
    {
        objectId: 0,
        drawingData: 1
    };

    this.objectId = objectId;
    this.drawingData = drawingData;
}

UndoRedoDataGraphicObjects.prototype = {
    getType : function ()
    {
        return UndoRedoDataTypes.GraphicObjects;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.objectId:
                return this.objectId;
            case this.Properties.drawingData:
                return this.drawingData;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.objectId: this.objectId = value;break;
            case this.Properties.drawingData: this.drawingData = value;break;
        }
    }
};

function UndoRedoDataGOPairProps(oldValue1, oldValue2, newValue1, newValue2)
{
    this.Properties =
    {
        oldValue1: 0,
        oldValue2: 1,

        newValue1: 2,
        newValue2: 3
    };

    this.oldValue1 = oldValue1;
    this.oldValue2 = oldValue2;

    this.newValue1 = newValue1;
    this.newValue2 = newValue2;
}

UndoRedoDataGOPairProps.prototype = {
    getType : function ()
    {
        return UndoRedoDataTypes.GOPairProps;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.oldValue1:
                return this.oldValue1;
            case this.Properties.oldValue2:
                return this.oldValue2;
            case this.Properties.newValue1:
                return this.newValue1;
            case this.Properties.newValue2:
                return this.newValue2;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.oldValue1: this.oldValue1 = value; break;
            case this.Properties.oldValue2: this.oldValue2 = value; break;
            case this.Properties.newValue1: this.newValue1 = value; break;
            case this.Properties.newValue2: this.newValue2 = value; break;
        }
    }
};


function UndoRedoDataGOSingleProp(oldValue, newValue)
{
    this.Properties =
    {
        oldValue: 0,
        newValue: 1
    };

    this.oldValue = oldValue;
    this.newValue = newValue;

}

UndoRedoDataGOSingleProp.prototype = {
    getType : function ()
    {
        return UndoRedoDataTypes.GOSingleProp;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.oldValue:
                return this.oldValue;
            case this.Properties.newValue:
                return this.newValue;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.oldValue: this.oldValue = value; break;
            case this.Properties.newValue: this.newValue = value; break;
        }
    }
};


function UndoRedoDataShapeRecalc()
{
    this.Properties =
    {
    };


}

UndoRedoDataShapeRecalc.prototype = {
    getType : function ()
    {
        return UndoRedoDataTypes.GOShapeRecalcTransform;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        return null;
    },
    setProperty : function (nType, value)
    {
    }
};

function UndoRedoDataAddAdjustment(name, val)
{
    this.Properties =
    {
        name: 0,
        val : 1
    };

    this.name = name;
    this.val = val;
}

UndoRedoDataAddAdjustment.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOAddAdjustment;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.name: return this.name;
            case this.Properties.val: return this.val;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.name: this.name = value; break;
            case this.Properties.val:  this.val = value; break;
        }
    }
};



function UndoRedoDataAddGuide(name, formula, x, y, z)
{
    this.Properties =
    {
        name: 0,
        formula : 1,
        x: 2,
        y: 3,
        z: 4
    };

    this.name = name;
    this.formula = formula;
    this.x = x;
    this.y = y;
    this.z = z;
}

UndoRedoDataAddGuide.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOAddGuide;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.name: return this.name;
            case this.Properties.formula: return this.formula;
            case this.Properties.x: return this.x;
            case this.Properties.y: return this.y;
            case this.Properties.z: return this.z;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.name: this.name = value; break;
            case this.Properties.formula: this.formula = value; break;
            case this.Properties.x: this.x = value; break;
            case this.Properties.y: this.y = value; break;
            case this.Properties.z: this.z = value; break;
        }
    }
};


function UndoRedoDataAddCnx(ang, x, y)
{
    this.Properties =
    {
        ang: 0,
        x : 1,
        y: 2
    };

    this.ang = ang;
    this.x = x;
    this.y = y;
}

UndoRedoDataAddCnx.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOAddCnx;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.ang: return this.ang;
            case this.Properties.x: return this.x;
            case this.Properties.y: return this.y;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.ang: this.ang = value; break;
            case this.Properties.x: this.x = value; break;
            case this.Properties.y: this.y = value; break;
        }
    }
};

function UndoRedoDataAddHandleXY(gdRefX, minX, maxX, gdRefY, minY, maxY, posX, posY)
{
    this.Properties =
    {
        gdRefX: 0,
        minX : 1,
        maxX: 2,

        gdRefY: 3,
        minY: 4,
        maxY: 5,
        posX: 6,
        posY: 7
    };

    this.gdRefX = gdRefX;
    this.maxX = maxX;
    this.minX = minX;


    this.gdRefY = gdRefY;
    this.maxY = maxY;
    this.minY = minY;
    this.posX = posX;
    this.posY = posY;
}

UndoRedoDataAddHandleXY.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOHandleXY;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.gdRefX: return this.gdRefX;
            case this.Properties.minX: return this.minX;
            case this.Properties.maxX: return this.maxX;
            case this.Properties.gdRefY: return this.gdRefY;
            case this.Properties.minY: return this.minY;
            case this.Properties.maxY: return this.maxY;
            case this.Properties.posX: return this.posX;
            case this.Properties.posY: return this.posY;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.gdRefX: this.gdRefX = value; break;
            case this.Properties.minX: this.minX = value; break;
            case this.Properties.maxX: this.maxX = value; break;
            case this.Properties.gdRefY: this.gdRefY = value; break;
            case this.Properties.minY: this.minY = value; break;
            case this.Properties.maxY: this.maxY = value; break;
            case this.Properties.posX: this.posX = value; break;
            case this.Properties.posY: this.posY = value; break;
        }
    }
};


function UndoRedoDataAddHandlePolar(gdRefR, minR, maxR, gdRefAng, minAng, maxAng, posX, posY)
{
    this.Properties =
    {
        gdRefR: 0,
        minR : 1,
        maxR: 2,

        gdRefAng: 3,
        minAng: 4,
        maxAng: 5,
        posX: 6,
        posY: 7
    };

    this.gdRefR = gdRefR;
    this.maxR = maxR;
    this.minR = minR;


    this.gdRefAng = gdRefAng;
    this.maxAng = maxAng;
    this.minAng = minAng;
    this.posX = posX;
    this.posY = posY;
}

UndoRedoDataAddHandlePolar.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOHandlePolar;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.gdRefR: return this.gdRefR;
            case this.Properties.minR: return this.minR;
            case this.Properties.maxR: return this.maxR;
            case this.Properties.gdRefAng: return this.gdRefAng;
            case this.Properties.minAng: return this.minAng;
            case this.Properties.maxAng: return this.maxAng;
            case this.Properties.posX: return this.posX;
            case this.Properties.posY: return this.posY;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.gdRefR: this.gdRefR = value; break;
            case this.Properties.minR: this.minR = value; break;
            case this.Properties.maxR: this.maxR = value; break;
            case this.Properties.gdRefAng: this.gdRefAng = value; break;
            case this.Properties.minAng: this.minAng = value; break;
            case this.Properties.maxAng: this.maxAng = value; break;
            case this.Properties.posX: this.posX = value; break;
            case this.Properties.posY: this.posY = value; break;
        }
    }
};


function UndoRedoDataAddPathCommand(command, x1, y1, x2, y2, x3, y3)
{
    this.Properties =
    {
        command: 0,
        x1: 1,
        y1: 2,
        x2: 3,
        y2: 4,
        x3: 5,
        y3: 6
    };
    this.command = command;
    this.x1 = x1;
    this.y1 = y1;
    this.x2 = x2;
    this.y2 = y2;
    this.x3 = x3;
    this.y3 = y3;
}

UndoRedoDataAddPathCommand.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOAddPathCommand;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.command: return this.command;
            case this.Properties.x1: return this.x1;
            case this.Properties.y1: return this.y1;
            case this.Properties.x2: return this.x2;
            case this.Properties.y2: return this.y2;
            case this.Properties.x3: return this.x3;
            case this.Properties.y3: return this.y3;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.command: this.command = value; break;
            case this.Properties.x1: this.x1 = value; break;
            case this.Properties.y1: this.y1 = value; break;
            case this.Properties.x2: this.x2 = value; break;
            case this.Properties.y2: this.y2 = value; break;
            case this.Properties.x3: this.x3 = value; break;
            case this.Properties.y3: this.y3 = value; break;
        }
    }
};


function UndoRedoDataAddObject(objectId)
{
    this.Properties =
    {
        objectId: 0
    };
    this.objectId = objectId;
}

UndoRedoDataAddObject.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOAddObject;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.objectId: return this.objectId;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.objectId: this.objectId = value; break;
        }
    }
};

function UndoRedoDataAddGeometryRect(l, t, r, b)
{
    this.Properties =
    {
        l: 0,
        t: 1,
        r: 2,
        b: 3
    };
    this.l = l;
    this.t = t;
    this.r = r;
    this.b = b;
}

UndoRedoDataAddGeometryRect.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOAddGeometryRect;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.l: return this.l;
            case this.Properties.t: return this.t;
            case this.Properties.r: return this.r;
            case this.Properties.b: return this.b;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.l: this.l = value; break;
            case this.Properties.t: this.t = value; break;
            case this.Properties.r: this.r = value; break;
            case this.Properties.b: this.b = value; break;

        }
    }
};
var g_oUndoRedoDataMoveToLineToProperties = {
        x: 0,
        y: 1,
        bMoveTo: 2
    };
function UndoRedoDataMoveToLineTo(x, y, bMoveTo)
{
    this.Properties = g_oUndoRedoDataMoveToLineToProperties;

    this.x = x;
    this.y = y;
    this.bMoveTo = bMoveTo;
}


UndoRedoDataMoveToLineTo.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOPathLineToMoveTo;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.x: return this.x;
            case this.Properties.y: return this.y;
            case this.Properties.bMoveTo: return this.bMoveTo;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.x: this.x = value; break;
            case this.Properties.y: this.y = value; break;
            case this.Properties.bMoveTo: this.bMoveTo = value; break;
        }
    }
};

var g_gUndoRedoDataArcToProperties = {
        wR: 0,
        hR: 1,
        stAng: 2,
        swAng: 3
    };
function UndoRedoDataArcTo(wR, hR, stAng, swAng)
{
    this.Properties = g_gUndoRedoDataArcToProperties;

    this.wR = wR;
    this.hR = hR;
    this.stAng = stAng;
    this.swAng = swAng;

}


UndoRedoDataArcTo.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOPathArcTo;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.wR: return this.wR;
            case this.Properties.hR: return this.hR;
            case this.Properties.stAng: return this.stAng;
            case this.Properties.swAng: return this.swAng;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.wR: this.wR = value; break;
            case this.Properties.hR: this.hR = value; break;
            case this.Properties.stAng: this.stAng = value; break;
            case this.Properties.swAng: this.swAng = value; break;
        }
    }
};
var g_oUndoRedoDataQuadBezToProperties = {
        x0: 0,
        y0: 1,
        x1: 2,
        y1: 3
    };
function UndoRedoDataQuadBezTo(x0, y0, x1, y1)
{
    this.Properties = g_oUndoRedoDataQuadBezToProperties;

    this.x0 = x0;
    this.y0 = y0;
    this.x1 = x1;
    this.y1 = y1;

}


UndoRedoDataQuadBezTo.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOPathQuadBezTo;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.x0: return this.x0;
            case this.Properties.y0: return this.y0;
            case this.Properties.x1: return this.x1;
            case this.Properties.y1: return this.y1;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.x0: this.x0 = value; break;
            case this.Properties.y0: this.y0 = value; break;
            case this.Properties.x1: this.x1 = value; break;
            case this.Properties.y1: this.y1 = value; break;
        }
    }
};

var g_oUndoRedoDataCubicBezToProperties = {
        x0: 0,
        y0: 1,
        x1: 2,
        y1: 3,
        x2: 4,
        y2: 5
    };
function UndoRedoDataCubicBezTo(x0, y0, x1, y1, x2, y2)
{
    this.Properties = g_oUndoRedoDataCubicBezToProperties;

    this.x0 = x0;
    this.y0 = y0;
    this.x1 = x1;
    this.y1 = y1;
    this.x2 = x2;
    this.y2 = y2;

}


UndoRedoDataCubicBezTo.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOPathCubicBezTo;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        switch (nType)
        {
            case this.Properties.x0: return this.x0;
            case this.Properties.y0: return this.y0;
            case this.Properties.x1: return this.x1;
            case this.Properties.y1: return this.y1;
            case this.Properties.x2: return this.x2;
            case this.Properties.y2: return this.y2;
        }
        return null;
    },
    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.x0: this.x0 = value; break;
            case this.Properties.y0: this.y0 = value; break;
            case this.Properties.x1: this.x1 = value; break;
            case this.Properties.y1: this.y1 = value; break;
            case this.Properties.x2: this.x2 = value; break;
            case this.Properties.y2: this.y2 = value; break;
        }
    }
};

var g_oUndoRedoDataClosePathProperties = {
    };
function UndoRedoDataClosePath()
{
    this.Properties = g_oUndoRedoDataClosePathProperties;

}


UndoRedoDataClosePath.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOPathClose;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {
        return null;
    },
    setProperty : function (nType, value)
    {

    }
};
var g_oUndoRedoDataSetAdjustmentValueProperties = {
        gdName:0,
        oldVal: 1,
        newVal: 2
    };
function UndoRedoDataSetAdjustmentValue(gdName, oldVal, newVal)
{
    this.Properties = g_oUndoRedoDataSetAdjustmentValueProperties;

    this.gdName = gdName;
    this.oldVal = oldVal;
    this.newVal = newVal;
}


UndoRedoDataSetAdjustmentValue.prototype =
{
    getType : function ()
    {
        return UndoRedoDataTypes.GOSetAdjustmentValue;
    },
    getProperties : function ()
    {
        return this.Properties;
    },
    getProperty : function (nType)
    {

        switch (nType)
        {
            case this.Properties.gdName: return this.gdName;
            case this.Properties.oldVal: return this.oldVal;
            case this.Properties.newVal: return this.newVal;
        }
        return null;
    },

    setProperty : function (nType, value)
    {
        switch (nType)
        {
            case this.Properties.gdName: this.gdName = value; break;
            case this.Properties.oldVal: this.oldVal = value; break;
            case this.Properties.newVal: this.newVal = value; break;
        }
    }
};

function UndoRedoWorkbook(wb)
{
	this.wb = wb;
	this.nType = UndoRedoClassTypes.Add(function(){return AscCommonExcel.g_oUndoRedoWorkbook;});
}

UndoRedoWorkbook.prototype = {
	getClassType : function()
	{
		return this.nType;
	},
	Undo : function(Type, Data, nSheetId, opt_wb)
	{
		this.UndoRedo(Type, Data, nSheetId, true, opt_wb);
	},
	Redo : function(Type, Data, nSheetId, opt_wb)
	{
		this.UndoRedo(Type, Data, nSheetId, false, opt_wb);
	},
	UndoRedo : function(Type, Data, nSheetId, bUndo, opt_wb)
	{
		var wb = opt_wb ? opt_wb : this.wb;
		var bNeedTrigger = true;
		if(AscCH.historyitem_Workbook_SheetAdd == Type)
		{
			if(null == Data.insertBefore)
				Data.insertBefore = 0;
			if(bUndo)
			{
				var outputParams = {sheet: null};
				wb.removeWorksheet(Data.insertBefore, outputParams);
				//сохраняем тот sheet который удалили, иначе может возникнуть ошибка, если какой-то обьект запоминал ссылку на sheet(например):
				//Добавляем лист  -> Добавляем ссылку -> undo -> undo -> redo -> redo
				Data.sheet = outputParams.sheet;
			}
			else
			{
				if(null != Data.sheet)
				{
					//сюда заходим только если до этого было сделано Undo
					wb.insertWorksheet(Data.insertBefore, Data.sheet);
				}
				else
				{
					if(null == Data.sheetidfrom)
						wb.createWorksheet(Data.insertBefore, Data.name, Data.sheetid);
					else
					{
						var oCurWorksheet = wb.getWorksheetById(Data.sheetidfrom);
						var nIndex = oCurWorksheet.getIndex();
						wb.copyWorksheet(nIndex, Data.insertBefore, Data.name, Data.sheetid, true, Data.tableNames);
					}
				}
			}
			wb.handlers.trigger("updateWorksheetByModel");
		}
		else if(AscCH.historyitem_Workbook_SheetRemove == Type)
		{
			if(bUndo)
			{
				wb.insertWorksheet(Data.index, Data.sheet);
			}
			else
			{
				var nIndex = Data.index;
				if(null == nIndex)
				{
					var oCurWorksheet = wb.getWorksheetById(Data.sheetId);
					if (oCurWorksheet)
						nIndex = oCurWorksheet.getIndex();
				}
				if(null != nIndex)
				{
					wb.removeWorksheet(nIndex);
				}
			}
			wb.handlers.trigger("updateWorksheetByModel");
		}
		else if(AscCH.historyitem_Workbook_SheetMove == Type)
		{
			if(bUndo)
			{
				wb.replaceWorksheet(Data.to, Data.from);
			}
			else
			{
				wb.replaceWorksheet(Data.from, Data.to);
			}
			wb.handlers.trigger("updateWorksheetByModel");
		}
		else if(AscCH.historyitem_Workbook_ChangeColorScheme == Type)
		{
			bNeedTrigger = false;
			if(bUndo)
				wb.theme.themeElements.clrScheme = Data.oldVal;
			else
				wb.theme.themeElements.clrScheme = Data.newVal;
			wb.rebuildColors();
			wb.oApi.asc_AfterChangeColorScheme();
		}
		else if (AscCH.historyitem_Workbook_DefinedNamesChange === Type || AscCH.historyitem_Workbook_DefinedNamesChangeUndo === Type) {
			var oldName, newName;
			if (bUndo) {
				oldName = Data.to;
				newName = Data.from;
			} else {
				if (wb.bCollaborativeChanges) {
					wb.handlers.trigger("asc_onLockDefNameManager", Asc.c_oAscDefinedNameReason.OK);
				}
				oldName = Data.from;
				newName = Data.to;
			}
			if (bUndo || AscCH.historyitem_Workbook_DefinedNamesChangeUndo !== Type) {
				if (null == newName) {
					wb.delDefinesNamesUndoRedo(oldName);
					wb.handlers.trigger("asc_onDelDefName")
				} else {
					wb.editDefinesNamesUndoRedo(oldName, newName);
					wb.handlers.trigger("asc_onEditDefName", oldName, newName);
				}
			}
		}
	},
	forwardTransformationIsAffect : function(Type) {
		return AscCH.historyitem_Workbook_SheetAdd === Type || AscCH.historyitem_Workbook_SheetRemove === Type ||
			AscCH.historyitem_Workbook_SheetMove === Type || AscCH.historyitem_Workbook_DefinedNamesChange === Type;
	},
	forwardTransformationGet : function(Type, Data, nSheetId) {
		if (AscCH.historyitem_Workbook_DefinedNamesChange === Type) {
			if(Data.newName && Data.newName.Ref){
				return {formula: Data.newName.Ref};
			}
		} else if(AscCH.historyitem_Workbook_SheetAdd === Type) {
			return {name: Data.name};
		}
		return null;
	},
	forwardTransformationSet : function(Type, Data, nSheetId, getRes) {
		if(AscCH.historyitem_Workbook_SheetAdd === Type) {
			Data.name = getRes.name;
		} else if (AscCH.historyitem_Cell_ChangeValue === Type) {
			if(Data && Data.newName){
				Data.newName.Ref = getRes.formula;
			}
		}
		return null;
	}
};

function UndoRedoCell(wb)
{
	this.wb = wb;
	this.nType = UndoRedoClassTypes.Add(function(){return AscCommonExcel.g_oUndoRedoCell;});
}
UndoRedoCell.prototype = {
	getClassType : function()
	{
		return this.nType;
	},
	Undo : function(Type, Data, nSheetId)
	{
		this.UndoRedo(Type, Data, nSheetId, true);
	},
	Redo : function(Type, Data, nSheetId)
	{
		this.UndoRedo(Type, Data, nSheetId, false);
	},
	UndoRedo : function(Type, Data, nSheetId, bUndo)
	{
		var ws = this.wb.getWorksheetById(nSheetId);
		if(null == ws)
			return;
		var nRow = Data.nRow;
		var nCol = Data.nCol;
		if(false != this.wb.bCollaborativeChanges)
		{
			var collaborativeEditing = this.wb.oApi.collaborativeEditing;
			nRow = collaborativeEditing.getLockOtherRow2(nSheetId, nRow);
			nCol = collaborativeEditing.getLockOtherColumn2(nSheetId, nCol);
			var oLockInfo = new AscCommonExcel.asc_CLockInfo();
			oLockInfo["sheetId"] = nSheetId;
			oLockInfo["type"] = c_oAscLockTypeElem.Range;
			oLockInfo["rangeOrObjectId"] = new Asc.Range(nCol, nRow, nCol, nRow);
			this.wb.aCollaborativeChangeElements.push(oLockInfo);
		}
		var cell =  ws._getCell(nRow, nCol);
		var Val;
		if(bUndo)
			Val = Data.oOldVal;
		else
			Val = Data.oNewVal;
		if(AscCH.historyitem_Cell_Fontname == Type)
			cell.setFontname(Val);
		else if(AscCH.historyitem_Cell_Fontsize == Type)
			cell.setFontsize(Val);
		else if(AscCH.historyitem_Cell_Fontcolor == Type)
			cell.setFontcolor(Val);
		else if(AscCH.historyitem_Cell_Bold == Type)
			cell.setBold(Val);
		else if(AscCH.historyitem_Cell_Italic == Type)
			cell.setItalic(Val);
		else if(AscCH.historyitem_Cell_Underline == Type)
			cell.setUnderline(Val);
		else if(AscCH.historyitem_Cell_Strikeout == Type)
			cell.setStrikeout(Val);
		else if(AscCH.historyitem_Cell_FontAlign == Type)
			cell.setFontAlign(Val);
		else if(AscCH.historyitem_Cell_AlignVertical == Type)
			cell.setAlignVertical(Val);
		else if(AscCH.historyitem_Cell_AlignHorizontal == Type)
			cell.setAlignHorizontal(Val);
		else if(AscCH.historyitem_Cell_Fill == Type)
			cell.setFill(Val);
		else if(AscCH.historyitem_Cell_Border == Type)
		{
			if(null != Val)
				cell.setBorder(Val.clone());
			else
				cell.setBorder(null);
		}
		else if(AscCH.historyitem_Cell_ShrinkToFit == Type)
			cell.setFill(Val);
		else if(AscCH.historyitem_Cell_Wrap == Type)
			cell.setWrap(Val);
		else if(AscCH.historyitem_Cell_Num == Type)
			cell.setNum(Val);
        else if(AscCH.historyitem_Cell_Angle == Type)
            cell.setAngle(Val);
        else if(AscCH.historyitem_Cell_ChangeArrayValueFormat == Type)
		{
			cell.oValue.multiText = [];
			for(var i = 0, length = Val.length; i < length; ++i)
				cell.oValue.multiText.push(Val[i].clone());
		}
		else if(AscCH.historyitem_Cell_ChangeValue === Type || AscCH.historyitem_Cell_ChangeValueUndo === Type)
		{
			if (bUndo || AscCH.historyitem_Cell_ChangeValueUndo !== Type) {
				cell.setValueData(Val);
			}
		}
		else if(AscCH.historyitem_Cell_SetStyle == Type)
		{
            if(null != Val)
                cell.setStyle(Val);
			else
				cell.setStyle(null);
		}
		else if(AscCH.historyitem_Cell_SetFont == Type)
		{
			cell.setFont(Val);
		}
		else if(AscCH.historyitem_Cell_SetQuotePrefix == Type)
		{
			cell.setQuotePrefix(Val);
		}
		else if(AscCH.historyitem_Cell_SetPivotButton == Type)
		{
			cell.setPivotButton(Val);
		}
		else if (AscCH.historyitem_Cell_Style == Type)
		{
			cell.setCellStyle(Val);
		}
	},
	forwardTransformationGet : function(Type, Data, nSheetId) {
		if (AscCH.historyitem_Cell_ChangeValue === Type && Data.oNewVal && Data.oNewVal.formula) {
			return {formula: Data.oNewVal.formula};
		}
		return null;
	},
	forwardTransformationSet : function(Type, Data, nSheetId, getRes) {
		if (AscCH.historyitem_Cell_ChangeValue === Type) {
			if(Data && Data.oNewVal){
				Data.oNewVal.formula = getRes.formula;
			}
		}
		return null;
	}
};

function UndoRedoWoorksheet(wb){
	this.wb = wb;
	this.nType = UndoRedoClassTypes.Add(function(){return AscCommonExcel.g_oUndoRedoWorksheet;});
}
UndoRedoWoorksheet.prototype = {
	getClassType : function()
	{
		return this.nType;
	},
	Undo : function(Type, Data, nSheetId, opt_wb)
	{
		this.UndoRedo(Type, Data, nSheetId, true, opt_wb);
	},
	Redo : function(Type, Data, nSheetId, opt_wb)
	{
		this.UndoRedo(Type, Data, nSheetId, false, opt_wb);
	},
	UndoRedo : function(Type, Data, nSheetId, bUndo, opt_wb)
	{
		var wb = opt_wb ? opt_wb : this.wb;
		var worksheetView, nRow, nCol, oLockInfo, cell, index, from, to, range, r1, c1, r2, c2, temp, i, length, data;
		var bInsert, operType; // ToDo избавиться от этого
		var ws = wb.getWorksheetById(nSheetId);
		if(null == ws)
			return;
		var collaborativeEditing = wb.oApi.collaborativeEditing;
		if(AscCH.historyitem_Worksheet_RemoveCell == Type)
		{
			nRow = Data.nRow;
			nCol = Data.nCol;
			if(false != wb.bCollaborativeChanges)
			{
				nRow = collaborativeEditing.getLockOtherRow2(nSheetId, nRow);
				nCol = collaborativeEditing.getLockOtherColumn2(nSheetId, nCol);
				oLockInfo = new AscCommonExcel.asc_CLockInfo();
				oLockInfo["sheetId"] = nSheetId;
				oLockInfo["type"] = c_oAscLockTypeElem.Range;
				oLockInfo["rangeOrObjectId"] = new Asc.Range(nCol, nRow, nCol, nRow);
				wb.aCollaborativeChangeElements.push(oLockInfo);
			}
			if(bUndo)
			{
				var oValue = Data.oOldVal.value;
				var oStyle = Data.oOldVal.style;
				cell = ws._getCell(nRow, nCol);
				cell.setValueData(oValue);
				if(null != oStyle)
					cell.setStyle(oStyle);
				else
					cell.setStyle(null);
			}
			else
				ws._removeCell(nRow, nCol);
		}
		else if(AscCH.historyitem_Worksheet_ColProp == Type)
		{
			index = Data.index;
			if(false != wb.bCollaborativeChanges)
			{
			    if (AscCommonExcel.g_nAllColIndex == index) {
			        range = new Asc.Range(0, 0, gc_nMaxCol0, gc_nMaxRow0);
			    }
			    else {
			        index = collaborativeEditing.getLockOtherColumn2(nSheetId, index);
			        range = new Asc.Range(index, 0, index, gc_nMaxRow0);
			    }
			    oLockInfo = new AscCommonExcel.asc_CLockInfo();
			    oLockInfo["sheetId"] = nSheetId;
			    oLockInfo["type"] = c_oAscLockTypeElem.Range;
			    oLockInfo["rangeOrObjectId"] = range;
			    wb.aCollaborativeChangeElements.push(oLockInfo);
			}
			var col = ws._getCol(index);
			if(bUndo)
				col.setWidthProp(Data.oOldVal);
			else
				col.setWidthProp(Data.oNewVal);
		}
		else if(AscCH.historyitem_Worksheet_RowProp == Type)
		{
			index = Data.index;
			if(false != wb.bCollaborativeChanges)
			{
				index = collaborativeEditing.getLockOtherRow2(nSheetId, index);
				oLockInfo = new AscCommonExcel.asc_CLockInfo();
				oLockInfo["sheetId"] = nSheetId;
				oLockInfo["type"] = c_oAscLockTypeElem.Range;
				oLockInfo["rangeOrObjectId"] = new Asc.Range(0, index, gc_nMaxCol0, index);
				wb.aCollaborativeChangeElements.push(oLockInfo);
			}
			var row = ws._getRow(index);
			if(bUndo)
				row.setHeightProp(Data.oOldVal);
			else
				row.setHeightProp(Data.oNewVal);
			
			//нужно для того, чтобы грамотно выставлялись цвета в ф/т при ручном скрытии строк, затрагивающих ф/т(undo/redo)
			//TODO для случая скрытия строк фильтром(undo), может два раза вызываться функция setColorStyleTable - пересмотреть
			var workSheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			workSheetView.model.autoFilters.reDrawFilter(null, index);
		}
		else if(AscCH.historyitem_Worksheet_RowHide == Type)
		{
			from = Data.from;
			to = Data.to;
			nRow = Data.bRow;
			
			if(false != wb.bCollaborativeChanges)
			{
				from = collaborativeEditing.getLockOtherRow2(nSheetId, from);
				to = collaborativeEditing.getLockOtherRow2(nSheetId, to);
				
				oLockInfo = new AscCommonExcel.asc_CLockInfo();
				oLockInfo["sheetId"] = nSheetId;
				oLockInfo["type"] = c_oAscLockTypeElem.Range;
				oLockInfo["rangeOrObjectId"] = new Asc.Range(0, from, gc_nMaxCol0, to);
				wb.aCollaborativeChangeElements.push(oLockInfo);
			}
			
			if(bUndo)
				nRow = !nRow;
			
			ws.setRowHidden(nRow, from, to);
			
			var workSheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			workSheetView.model.autoFilters.reDrawFilter(new Asc.Range(0, from, ws.nColsCount - 1, to));
		}
		else if(AscCH.historyitem_Worksheet_AddRows == Type || AscCH.historyitem_Worksheet_RemoveRows == Type)
		{
			from = Data.from;
			to = Data.to;
			if(false != wb.bCollaborativeChanges)
			{
				from = collaborativeEditing.getLockOtherRow2(nSheetId, from);
				to = collaborativeEditing.getLockOtherRow2(nSheetId, to);
				if(false == ((true == bUndo && AscCH.historyitem_Worksheet_AddRows == Type) || (false == bUndo && AscCH.historyitem_Worksheet_RemoveRows == Type)))
				{
					oLockInfo = new AscCommonExcel.asc_CLockInfo();
					oLockInfo["sheetId"] = nSheetId;
					oLockInfo["type"] = c_oAscLockTypeElem.Range;
					oLockInfo["rangeOrObjectId"] = new Asc.Range(0, from, gc_nMaxCol0, to);
					wb.aCollaborativeChangeElements.push(oLockInfo);
				}
			}
			range = Asc.Range(0, from, gc_nMaxCol0, to);
			if((true == bUndo && AscCH.historyitem_Worksheet_AddRows == Type) || (false == bUndo && AscCH.historyitem_Worksheet_RemoveRows == Type)) {
				ws.removeRows(from, to);
				bInsert = false;
				operType = c_oAscDeleteOptions.DeleteRows;
			} else {
				ws.insertRowsBefore(from, to - from + 1);
				bInsert = true;
				operType = c_oAscInsertOptions.InsertRows;
			}

			// Нужно поменять пересчетные индексы для совместного редактирования (lock-элементы), но только если это не изменения от другого пользователя
			if (true !== wb.bCollaborativeChanges)
				ws.workbook.handlers.trigger("undoRedoAddRemoveRowCols", nSheetId, Type, range, bUndo);

			// ToDo Так делать неправильно, нужно поправить (перенести логику в model, а отрисовку отделить)
			worksheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			worksheetView.cellCommentator.updateCommentsDependencies(bInsert, operType, range);
		}
		else if(AscCH.historyitem_Worksheet_AddCols == Type || AscCH.historyitem_Worksheet_RemoveCols == Type)
		{
			from = Data.from;
			to = Data.to;
			if(false != wb.bCollaborativeChanges)
			{
				from = collaborativeEditing.getLockOtherColumn2(nSheetId, from);
				to = collaborativeEditing.getLockOtherColumn2(nSheetId, to);
				if(false == ((true == bUndo && AscCH.historyitem_Worksheet_AddCols == Type) || (false == bUndo && AscCH.historyitem_Worksheet_RemoveCols == Type)))
				{
					oLockInfo = new AscCommonExcel.asc_CLockInfo();
					oLockInfo["sheetId"] = nSheetId;
					oLockInfo["type"] = c_oAscLockTypeElem.Range;
					oLockInfo["rangeOrObjectId"] = new Asc.Range(from, 0, to, gc_nMaxRow0);
					wb.aCollaborativeChangeElements.push(oLockInfo);
				}
			}

			range = Asc.Range(from, 0, to, gc_nMaxRow0);
			if((true == bUndo && AscCH.historyitem_Worksheet_AddCols == Type) || (false == bUndo && AscCH.historyitem_Worksheet_RemoveCols == Type)) {
				ws.removeCols(from, to);
				bInsert = false;
				operType = c_oAscDeleteOptions.DeleteColumns;
			} else {
				ws.insertColsBefore(from, to - from + 1);
				bInsert = true;
				operType = c_oAscInsertOptions.InsertColumns;
			}

			// Нужно поменять пересчетные индексы для совместного редактирования (lock-элементы), но только если это не изменения от другого пользователя
			if (true !== wb.bCollaborativeChanges)
				ws.workbook.handlers.trigger("undoRedoAddRemoveRowCols", nSheetId, Type, range, bUndo);

			// ToDo Так делать неправильно, нужно поправить (перенести логику в model, а отрисовку отделить)
			worksheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			worksheetView.cellCommentator.updateCommentsDependencies(bInsert, operType, range);
		}
		else if(AscCH.historyitem_Worksheet_ShiftCellsLeft == Type || AscCH.historyitem_Worksheet_ShiftCellsRight == Type)
		{
			r1 = Data.r1;
			c1 = Data.c1;
			r2 = Data.r2;
			c2 = Data.c2;
			if(false != wb.bCollaborativeChanges)
			{
				r1 = collaborativeEditing.getLockOtherRow2(nSheetId, r1);
				c1 = collaborativeEditing.getLockOtherColumn2(nSheetId, c1);
				r2 = collaborativeEditing.getLockOtherRow2(nSheetId, r2);
				c2 = collaborativeEditing.getLockOtherColumn2(nSheetId, c2);
				if(false == ((true == bUndo && AscCH.historyitem_Worksheet_ShiftCellsLeft == Type) || (false == bUndo && AscCH.historyitem_Worksheet_ShiftCellsRight == Type)))
				{
					oLockInfo = new AscCommonExcel.asc_CLockInfo();
					oLockInfo["sheetId"] = nSheetId;
					oLockInfo["type"] = c_oAscLockTypeElem.Range;
					oLockInfo["rangeOrObjectId"] = new Asc.Range(c1, r1, c2, r2);
					wb.aCollaborativeChangeElements.push(oLockInfo);
				}
			}

			range = ws.getRange3(r1, c1, r2, c2);
			if((true == bUndo && AscCH.historyitem_Worksheet_ShiftCellsLeft == Type) || (false == bUndo && AscCH.historyitem_Worksheet_ShiftCellsRight == Type)) {
				range.addCellsShiftRight();
				bInsert = true;
				operType = c_oAscInsertOptions.InsertCellsAndShiftRight;
			}  else {
				range.deleteCellsShiftLeft();
				bInsert = false;
				operType = c_oAscDeleteOptions.DeleteCellsAndShiftLeft;
			}

			// ToDo Так делать неправильно, нужно поправить (перенести логику в model, а отрисовку отделить)
			worksheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			worksheetView.cellCommentator.updateCommentsDependencies(bInsert, operType, range.bbox);
		}
		else if(AscCH.historyitem_Worksheet_ShiftCellsTop == Type || AscCH.historyitem_Worksheet_ShiftCellsBottom == Type)
		{
			r1 = Data.r1;
			c1 = Data.c1;
			r2 = Data.r2;
			c2 = Data.c2;
			if(false != wb.bCollaborativeChanges)
			{
				r1 = collaborativeEditing.getLockOtherRow2(nSheetId, r1);
				c1 = collaborativeEditing.getLockOtherColumn2(nSheetId, c1);
				r2 = collaborativeEditing.getLockOtherRow2(nSheetId, r2);
				c2 = collaborativeEditing.getLockOtherColumn2(nSheetId, c2);
				if(false == ((true == bUndo && AscCH.historyitem_Worksheet_ShiftCellsTop == Type) || (false == bUndo && AscCH.historyitem_Worksheet_ShiftCellsBottom == Type)))
				{
					oLockInfo = new AscCommonExcel.asc_CLockInfo();
					oLockInfo["sheetId"] = nSheetId;
					oLockInfo["type"] = c_oAscLockTypeElem.Range;
					oLockInfo["rangeOrObjectId"] = new Asc.Range(c1, r1, c2, r2);
					wb.aCollaborativeChangeElements.push(oLockInfo);
				}
			}

			range = ws.getRange3(r1, c1, r2, c2);
			if((true == bUndo && AscCH.historyitem_Worksheet_ShiftCellsTop == Type) || (false == bUndo && AscCH.historyitem_Worksheet_ShiftCellsBottom == Type)) {
				range.addCellsShiftBottom();
				bInsert = true;
				operType = c_oAscInsertOptions.InsertCellsAndShiftDown;
			} else {
				range.deleteCellsShiftUp();
				bInsert = false;
				operType = c_oAscDeleteOptions.DeleteCellsAndShiftTop;
			}

			// ToDo Так делать неправильно, нужно поправить (перенести логику в model, а отрисовку отделить)
			worksheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			worksheetView.cellCommentator.updateCommentsDependencies(bInsert, operType, range.bbox);
		}
		else if(AscCH.historyitem_Worksheet_Sort == Type)
		{
			var bbox = Data.bbox;
			var places = Data.places;
			if(false != wb.bCollaborativeChanges)
			{
				bbox.r1 = collaborativeEditing.getLockOtherRow2(nSheetId, bbox.r1);
				bbox.c1 = collaborativeEditing.getLockOtherColumn2(nSheetId, bbox.c1);
				bbox.r2 = collaborativeEditing.getLockOtherRow2(nSheetId, bbox.r2);
				bbox.c2 = collaborativeEditing.getLockOtherColumn2(nSheetId, bbox.c2);
				for(i = 0, length = Data.places.length; i < length; ++i)
				{
					var place = Data.places[i];
					place.from = collaborativeEditing.getLockOtherRow2(nSheetId, place.from);
					place.to = collaborativeEditing.getLockOtherRow2(nSheetId, place.to);
					oLockInfo = new AscCommonExcel.asc_CLockInfo();
					oLockInfo["sheetId"] = nSheetId;
					oLockInfo["type"] = c_oAscLockTypeElem.Range;
					oLockInfo["rangeOrObjectId"] = new Asc.Range(bbox.c1, place.from, bbox.c2, place.from);
					wb.aCollaborativeChangeElements.push(oLockInfo);
				}
			}
			range = ws.getRange3(bbox.r1, bbox.c1, bbox.r2, bbox.c2);
			range._sortByArray(bbox, places);
			
			worksheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			worksheetView.model.autoFilters.resetTableStyles(bbox);
		}
		else if(AscCH.historyitem_Worksheet_MoveRange == Type)
		{
			//todo worksheetView.autoFilters._moveAutoFilters(worksheetView ,null, null, g_oUndoRedoAutoFiltersMoveData);
			from = Asc.Range(Data.from.c1, Data.from.r1, Data.from.c2, Data.from.r2);
			to = Asc.Range(Data.to.c1, Data.to.r1, Data.to.c2, Data.to.r2);
            var copyRange = Data.copyRange;

			if(bUndo)
			{
				temp = from;
				from = to;
				to = temp;
			}
			if(false != wb.bCollaborativeChanges)
			{
				var coBBoxTo 	= Asc.Range(0, 0, 0, 0),
					coBBoxFrom 	= Asc.Range(0, 0, 0, 0);

				coBBoxTo.r1 = collaborativeEditing.getLockOtherRow2(	nSheetId, to.r1);
				coBBoxTo.c1 = collaborativeEditing.getLockOtherColumn2(	nSheetId, to.c1);
				coBBoxTo.r2 = collaborativeEditing.getLockOtherRow2(	nSheetId, to.r2);
				coBBoxTo.c2 = collaborativeEditing.getLockOtherColumn2(	nSheetId, to.c2);

				coBBoxFrom.r1 = collaborativeEditing.getLockOtherRow2(		nSheetId, from.r1);
				coBBoxFrom.c1 = collaborativeEditing.getLockOtherColumn2(	nSheetId, from.c1);
				coBBoxFrom.r2 = collaborativeEditing.getLockOtherRow2(		nSheetId, from.r2);
				coBBoxFrom.c2 = collaborativeEditing.getLockOtherColumn2(	nSheetId, from.c2);

				ws._moveRange(coBBoxFrom, coBBoxTo, copyRange);
			}
			else{
				ws._moveRange(from, to, copyRange);
			}
			worksheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			if(bUndo)//если на Undo перемещается диапазон из форматированной таблицы - стиль форматированной таблицы не должен цепляться
			{
				worksheetView.model.autoFilters._cleanStyleTable(to);
			}

			worksheetView.model.autoFilters.reDrawFilter(to);
			worksheetView.model.autoFilters.reDrawFilter(from);
		}
		else if(AscCH.historyitem_Worksheet_Rename == Type)
		{
			if (bUndo) {
				ws.setName(Data.from, true);
			} else {
				ws.setName(Data.to, true);
			}
		}
		else if(AscCH.historyitem_Worksheet_Hide == Type)
		{
			if(bUndo)
				ws.setHidden(Data.from);
			else
				ws.setHidden(Data.to);
		}
		else if(AscCH.historyitem_Worksheet_CreateRow == Type)
		{
			if(bUndo)
				ws._removeRow(Data.elem);
			else
				ws._getRow(Data.elem);
		}
		else if(AscCH.historyitem_Worksheet_CreateCol == Type)
		{
			if(bUndo)
				ws._removeCol(Data.elem);
			else
				ws._getCol(Data.elem);
		}
		else if(AscCH.historyitem_Worksheet_CreateCell == Type)
		{
			if(bUndo)
				ws._removeCell(Data.nRow, Data.nCol);
			else
				ws._getCell(Data.nRow, Data.nCol);
		}
        else if (AscCH.historyitem_Worksheet_SetDisplayGridlines === Type) {
			ws.setDisplayGridlines(bUndo ? Data.from : Data.to);
		} else if (AscCH.historyitem_Worksheet_SetDisplayHeadings === Type) {
			ws.setDisplayHeadings(bUndo ? Data.from : Data.to);
		}
		else if(AscCH.historyitem_Worksheet_ChangeMerge === Type){
			from = null;
			if (null != Data.from && null != Data.from.r1 && null != Data.from.c1 && null != Data.from.r2 && null != Data.from.c2) {
				from = new Asc.Range(Data.from.c1, Data.from.r1, Data.from.c2, Data.from.r2);
				if (false != wb.bCollaborativeChanges) {
					from.r1 = collaborativeEditing.getLockOtherRow2(nSheetId, from.r1);
					from.c1 = collaborativeEditing.getLockOtherColumn2(nSheetId, from.c1);
					from.r2 = collaborativeEditing.getLockOtherRow2(nSheetId, from.r2);
					from.c2 = collaborativeEditing.getLockOtherColumn2(nSheetId, from.c2);
				}
			}
			to = null;
			if (null != Data.to && null != Data.to.r1 && null != Data.to.c1 && null != Data.to.r2 && null != Data.to.c2) {
				to = new Asc.Range(Data.to.c1, Data.to.r1, Data.to.c2, Data.to.r2);
				if (false != wb.bCollaborativeChanges) {
					to.r1 = collaborativeEditing.getLockOtherRow2(nSheetId, to.r1);
					to.c1 = collaborativeEditing.getLockOtherColumn2(nSheetId, to.c1);
					to.r2 = collaborativeEditing.getLockOtherRow2(nSheetId, to.r2);
					to.c2 = collaborativeEditing.getLockOtherColumn2(nSheetId, to.c2);
				}
			}
			if(bUndo)
			{
				temp = from;
				from = to;
				to = temp;
			}
			if(null != from)
			{
				var aMerged = ws.mergeManager.get(from);
				for(i in aMerged.inner)
				{
					var merged = aMerged.inner[i];
					if(merged.bbox.isEqual(from))
					{
						ws.mergeManager.removeElement(merged);
						break;
					}
				}
			}
			data = 1;
			if(null != to)
				ws.mergeManager.add(to, data);
		}
		else if(AscCH.historyitem_Worksheet_ChangeHyperlink === Type) {
			from = null;
			if (null != Data.from && null != Data.from.r1 && null != Data.from.c1 && null != Data.from.r2 && null != Data.from.c2) {
				from = new Asc.Range(Data.from.c1, Data.from.r1, Data.from.c2, Data.from.r2);
				if (false != wb.bCollaborativeChanges) {
					from.r1 = collaborativeEditing.getLockOtherRow2(nSheetId, from.r1);
					from.c1 = collaborativeEditing.getLockOtherColumn2(nSheetId, from.c1);
					from.r2 = collaborativeEditing.getLockOtherRow2(nSheetId, from.r2);
					from.c2 = collaborativeEditing.getLockOtherColumn2(nSheetId, from.c2);
				}
			}
			to = null;
			if (null != Data.to && null != Data.to.r1 && null != Data.to.c1 && null != Data.to.r2 && null != Data.to.c2) {
				to = new Asc.Range(Data.to.c1, Data.to.r1, Data.to.c2, Data.to.r2);
				if (false != wb.bCollaborativeChanges) {
					to.r1 = collaborativeEditing.getLockOtherRow2(nSheetId, to.r1);
					to.c1 = collaborativeEditing.getLockOtherColumn2(nSheetId, to.c1);
					to.r2 = collaborativeEditing.getLockOtherRow2(nSheetId, to.r2);
					to.c2 = collaborativeEditing.getLockOtherColumn2(nSheetId, to.c2);
				}
			}
			if(bUndo)
			{
				temp = from;
				from = to;
				to = temp;
			}
			//не делаем clone потому что предполагаем, что здесь могут быть только операции изменения рзмеров, перемещение или удаления одной ссылки
			data = null;
			if(null != from)
			{
				var aHyperlinks = ws.hyperlinkManager.get(from);
				for(i in aHyperlinks.inner)
				{
					var hyp = aHyperlinks.inner[i];
					if(hyp.bbox.isEqual(from))
					{
						data = hyp.data;
						ws.hyperlinkManager.removeElement(hyp);
						break;
					}
				}
			}
			if(null == data)
				data = Data.hyperlink;
			if(null != data && null != to)
			{
				data.Ref = ws.getRange3(to.r1, to.c1, to.r2, to.c2);
				ws.hyperlinkManager.add(to, data);
			}
		}
        else if (AscCH.historyitem_Worksheet_ChangeFrozenCell === Type) {
			worksheetView = wb.oApi.wb.getWorksheetById(nSheetId);
			var updateData = bUndo ? Data.from : Data.to;
			worksheetView._updateFreezePane(updateData.c1, updateData.r1, /*lockDraw*/true);
		}
        else if (AscCH.historyitem_Worksheet_SetTabColor === Type) {
			ws.setTabColor(bUndo ? Data.from : Data.to);
		}
	},
	forwardTransformationIsAffect : function(Type) {
		return AscCH.historyitem_Worksheet_AddRows === Type || AscCH.historyitem_Worksheet_RemoveRows === Type ||
			AscCH.historyitem_Worksheet_AddCols === Type || AscCH.historyitem_Worksheet_RemoveCols === Type ||
			AscCH.historyitem_Worksheet_ShiftCellsLeft === Type || AscCH.historyitem_Worksheet_ShiftCellsRight === Type ||
			AscCH.historyitem_Worksheet_ShiftCellsTop === Type || AscCH.historyitem_Worksheet_ShiftCellsBottom === Type ||
			AscCH.historyitem_Worksheet_MoveRange === Type || AscCH.historyitem_Worksheet_Rename === Type;
	},
	forwardTransformationGet : function(Type, Data, nSheetId) {
		if (AscCH.historyitem_Worksheet_Rename === Type) {
			return {from: Data.from, name: Data.to};
		}
		return null;
	},
	forwardTransformationSet : function(Type, Data, nSheetId, getRes) {
		if(AscCH.historyitem_Worksheet_Rename === Type) {
			Data.from = getRes.from;
			Data.to = getRes.name;
		}
		return null;
	}
};

function UndoRedoRowCol(wb, bRow){
	this.wb = wb;
	this.bRow = bRow;
	this.nTypeRow = UndoRedoClassTypes.Add(function(){return AscCommonExcel.g_oUndoRedoRow;});
	this.nTypeCol = UndoRedoClassTypes.Add(function(){return AscCommonExcel.g_oUndoRedoCol;});
}
UndoRedoRowCol.prototype = {
	getClassType : function()
	{
		if(this.bRow)
			return this.nTypeRow;
		else
			return this.nTypeCol;
	},
	Undo : function(Type, Data, nSheetId)
	{
		this.UndoRedo(Type, Data, nSheetId, true);
	},
	Redo : function(Type, Data, nSheetId)
	{
		this.UndoRedo(Type, Data, nSheetId, false);
	},
	UndoRedo : function(Type, Data, nSheetId, bUndo)
	{
		var ws = this.wb.getWorksheetById(nSheetId);
		if(null == ws)
			return;
		var nIndex = Data.index;
		if(false != this.wb.bCollaborativeChanges)
		{
			var collaborativeEditing = this.wb.oApi.collaborativeEditing;
			var oLockInfo = new AscCommonExcel.asc_CLockInfo();
			oLockInfo["sheetId"] = nSheetId;
			oLockInfo["type"] = c_oAscLockTypeElem.Range;
			if(this.bRow)
			{
				nIndex = collaborativeEditing.getLockOtherRow2(nSheetId, nIndex);
				oLockInfo["rangeOrObjectId"] = new Asc.Range(0, nIndex, gc_nMaxCol0, nIndex);
			}
			else
			{
			    if (AscCommonExcel.g_nAllColIndex == nIndex) {
			        oLockInfo["rangeOrObjectId"] = new Asc.Range(0, 0, gc_nMaxCol0, gc_nMaxRow0);
			    }
			    else{
			        nIndex = collaborativeEditing.getLockOtherColumn2(nSheetId, nIndex);
			        oLockInfo["rangeOrObjectId"] = new Asc.Range(nIndex, 0, nIndex, gc_nMaxRow0);
			    }
			}
			this.wb.aCollaborativeChangeElements.push(oLockInfo);
		}
		var Val;
		if(bUndo)
			Val = Data.oOldVal;
		else
			Val = Data.oNewVal;
		var row;
		if(this.bRow)
			row = ws._getRow(nIndex);
		else
			row = ws._getCol(nIndex);
		if(AscCH.historyitem_RowCol_SetFont == Type)
			row.setFont(Val);
		else if(AscCH.historyitem_RowCol_Fontname == Type)
			row.setFontname(Val);
		else if(AscCH.historyitem_RowCol_Fontsize == Type)
			row.setFontsize(Val);
		else if(AscCH.historyitem_RowCol_Fontcolor == Type)
			row.setFontcolor(Val);
		else if(AscCH.historyitem_RowCol_Bold == Type)
			row.setBold(Val);
		else if(AscCH.historyitem_RowCol_Italic == Type)
			row.setItalic(Val);
		else if(AscCH.historyitem_RowCol_Underline == Type)
			row.setUnderline(Val);
		else if(AscCH.historyitem_RowCol_Strikeout == Type)
			row.setStrikeout(Val);
		else if(AscCH.historyitem_RowCol_FontAlign == Type)
			row.setFontAlign(Val);
		else if(AscCH.historyitem_RowCol_AlignVertical == Type)
			row.setAlignVertical(Val);
		else if(AscCH.historyitem_RowCol_AlignHorizontal == Type)
			row.setAlignHorizontal(Val);
		else if(AscCH.historyitem_RowCol_Fill == Type)
			row.setFill(Val);
		else if(AscCH.historyitem_RowCol_Border == Type)
		{
			if(null != Val)
				row.setBorder(Val.clone());
			else
				row.setBorder(null);
		}
		else if(AscCH.historyitem_RowCol_ShrinkToFit == Type)
			row.setShrinkToFit(Val);
		else if(AscCH.historyitem_RowCol_Wrap == Type)
			row.setWrap(Val);
		else if(AscCH.historyitem_RowCol_Num == Type)
			row.setNum(Val);
        else if(AscCH.historyitem_RowCol_Angle == Type)
            row.setAngle(Val);
		else if(AscCH.historyitem_RowCol_SetStyle == Type)
            row.setStyle(Val);
		else if (AscCH.historyitem_RowCol_SetCellStyle == Type)
			row.setCellStyle(Val);
	}
};

function UndoRedoComment(wb){
	this.wb = wb;
	this.nType = UndoRedoClassTypes.Add(function(){return AscCommonExcel.g_oUndoRedoComment;});
}
UndoRedoComment.prototype = {
	getClassType : function()
	{
		return this.nType;
	},
	Undo : function(Type, Data, nSheetId)
	{
		this.UndoRedo(Type, Data, nSheetId, true);
	},
	Redo : function(Type, Data, nSheetId)
	{
		this.UndoRedo(Type, Data, nSheetId, false);
	},
	UndoRedo : function (Type, Data, nSheetId, bUndo)
	{
		var oModel = (null == nSheetId) ? this.wb : this.wb.getWorksheetById(nSheetId);
		if (!oModel.aComments)
			oModel.aComments = [];

		var api = window["Asc"]["editor"];
		if (!api.wb)
			return;
		var ws = (null == nSheetId) ? api.wb : api.wb.getWorksheetById(nSheetId);
		Data.worksheet = ws;

		var cellCommentator = ws.cellCommentator;
		if ( bUndo == true )
			cellCommentator.Undo(Type, Data);
		else {
			var collaborativeEditing;
			// CCommentData
			if ( (Data.commentBefore == undefined) && (Data.commentAfter == undefined) ) {
				if ( !Data.bDocument ) {
					if ( false != this.wb.bCollaborativeChanges ) {
						collaborativeEditing = this.wb.oApi.collaborativeEditing;
						Data.nRow = collaborativeEditing.getLockOtherRow2(nSheetId, Data.nRow);
						Data.nCol = collaborativeEditing.getLockOtherColumn2(nSheetId, Data.nCol);
					}
				}
			} else {
				// CompositeCommentData
				if ( !Data.commentAfter.bDocument ) {
					if ( false != this.wb.bCollaborativeChanges ) {
						collaborativeEditing = this.wb.oApi.collaborativeEditing;
						Data.commentAfter.nRow = collaborativeEditing.getLockOtherRow2(nSheetId, Data.commentAfter.nRow);
						Data.commentAfter.nCol = collaborativeEditing.getLockOtherColumn2(nSheetId, Data.commentAfter.nCol);
					}
				}
			}

			cellCommentator.Redo(Type, Data);
		}
	}
};

function UndoRedoAutoFilters(wb){
	this.wb = wb;
	this.nType = UndoRedoClassTypes.Add(function(){return AscCommonExcel.g_oUndoRedoAutoFilters;});
}
UndoRedoAutoFilters.prototype = {
	getClassType : function() {
		return this.nType;
	},
	Undo : function (Type, Data, nSheetId, opt_wb) {
		this.UndoRedo(Type, Data, nSheetId, true, opt_wb);
	},
	Redo : function (Type, Data, nSheetId, opt_wb) {
		this.UndoRedo(Type, Data, nSheetId, false, opt_wb);
	},
	UndoRedo : function (Type, Data, nSheetId, bUndo, opt_wb) {
		var wb = opt_wb ? opt_wb : this.wb;
		var ws = wb.getWorksheetById(nSheetId);
		if(ws){
			var autoFilters = ws.autoFilters;
			if (bUndo === true)
			{
				autoFilters.Undo(Type, Data);
			}
			else
			{
				if(AscCH.historyitem_AutoFilter_ChangeColumnName === Type || AscCH.historyitem_AutoFilter_ChangeTotalRow === Type)
				{
					if(false != this.wb.bCollaborativeChanges)
					{
						var collaborativeEditing = this.wb.oApi.collaborativeEditing;
						Data.nRow = collaborativeEditing.getLockOtherRow2(nSheetId, Data.nRow);
						Data.nCol = collaborativeEditing.getLockOtherColumn2(nSheetId, Data.nCol);
					}
				}
				autoFilters.Redo(Type, Data);
			}
		}
	},
	forwardTransformationIsAffect : function(Type) {
		return AscCH.historyitem_AutoFilter_Add === Type || AscCH.historyitem_AutoFilter_ChangeTableName === Type ||
			AscCH.historyitem_AutoFilter_Empty === Type || AscCH.historyitem_AutoFilter_ChangeColumnName === Type;
	}
};

	function UndoRedoSparklines(wb) {
		this.wb = wb;
		this.nType = UndoRedoClassTypes.Add(function () {
			return AscCommonExcel.g_oUndoRedoSparklines;
		});
	}

	UndoRedoSparklines.prototype.getClassType = function () {
		return this.nType;
	};
	UndoRedoSparklines.prototype.Undo = function (Type, Data, nSheetId) {
		this.UndoRedo(Type, Data, nSheetId, true);
	};
	UndoRedoSparklines.prototype.Redo = function (Type, Data, nSheetId) {
		this.UndoRedo(Type, Data, nSheetId, false);
	};
	UndoRedoSparklines.prototype.UndoRedo = function (Type, Data, nSheetId, bUndo) {
	};

	function UndoRedoPivotTables(wb) {
		this.wb = wb;
		this.nType = UndoRedoClassTypes.Add(function () {
			return AscCommonExcel.g_oUndoRedoPivotTables;
		});
	}

	UndoRedoPivotTables.prototype.getClassType = function () {
		return this.nType;
	};
	UndoRedoPivotTables.prototype.Undo = function (Type, Data, nSheetId) {
		this.UndoRedo(Type, Data, nSheetId, true);
	};
	UndoRedoPivotTables.prototype.Redo = function (Type, Data, nSheetId) {
		this.UndoRedo(Type, Data, nSheetId, false);
	};
	UndoRedoPivotTables.prototype.UndoRedo = function (Type, Data, nSheetId, bUndo) {
		var wb = opt_wb ? opt_wb : this.wb;
		var ws = wb.getWorksheetById(nSheetId);
		if (ws) {

		}
	};

	//----------------------------------------------------------export----------------------------------------------------
	window['AscCommonExcel'] = window['AscCommonExcel'] || {};
	window['AscCommonExcel'].UndoRedoItemSerializable = UndoRedoItemSerializable;
	window['AscCommonExcel'].UndoRedoDataTypes = UndoRedoDataTypes;
	window['AscCommonExcel'].UndoRedoData_CellSimpleData = UndoRedoData_CellSimpleData;
	window['AscCommonExcel'].UndoRedoData_CellData = UndoRedoData_CellData;
	window['AscCommonExcel'].UndoRedoData_CellValueData = UndoRedoData_CellValueData;
	window['AscCommonExcel'].UndoRedoData_FromToRowCol = UndoRedoData_FromToRowCol;
	window['AscCommonExcel'].UndoRedoData_FromTo = UndoRedoData_FromTo;
	window['AscCommonExcel'].UndoRedoData_FromToHyperlink = UndoRedoData_FromToHyperlink;
	window['AscCommonExcel'].UndoRedoData_IndexSimpleProp = UndoRedoData_IndexSimpleProp;
	window['AscCommonExcel'].UndoRedoData_ColProp = UndoRedoData_ColProp;
	window['AscCommonExcel'].UndoRedoData_RowProp = UndoRedoData_RowProp;
	window['AscCommonExcel'].UndoRedoData_BBox = UndoRedoData_BBox;
	window['AscCommonExcel'].UndoRedoData_SortData = UndoRedoData_SortData;
	window['AscCommonExcel'].UndoRedoData_SheetAdd = UndoRedoData_SheetAdd;
	window['AscCommonExcel'].UndoRedoData_SheetRemove = UndoRedoData_SheetRemove;
	window['AscCommonExcel'].UndoRedoData_DefinedNames = UndoRedoData_DefinedNames;
	window['AscCommonExcel'].UndoRedoData_ClrScheme = UndoRedoData_ClrScheme;
	window['AscCommonExcel'].UndoRedoData_AutoFilter = UndoRedoData_AutoFilter;
	window['AscCommonExcel'].UndoRedoData_SingleProperty = UndoRedoData_SingleProperty;
	window['AscCommonExcel'].UndoRedoWorkbook = UndoRedoWorkbook;
	window['AscCommonExcel'].UndoRedoCell = UndoRedoCell;
	window['AscCommonExcel'].UndoRedoWoorksheet = UndoRedoWoorksheet;
	window['AscCommonExcel'].UndoRedoRowCol = UndoRedoRowCol;
	window['AscCommonExcel'].UndoRedoComment = UndoRedoComment;
	window['AscCommonExcel'].UndoRedoAutoFilters = UndoRedoAutoFilters;
	window['AscCommonExcel'].UndoRedoSparklines = UndoRedoSparklines;
	window['AscCommonExcel'].UndoRedoPivotTables = UndoRedoPivotTables;

	window['AscCommonExcel'].g_oUndoRedoWorkbook = null;
	window['AscCommonExcel'].g_oUndoRedoCell = null;
	window['AscCommonExcel'].g_oUndoRedoWorksheet = null;
	window['AscCommonExcel'].g_oUndoRedoRow = null;
	window['AscCommonExcel'].g_oUndoRedoCol = null;
	window['AscCommonExcel'].g_oUndoRedoComment = null;
	window['AscCommonExcel'].g_oUndoRedoAutoFilters = null;
	window['AscCommonExcel'].g_oUndoRedoSparklines = null;
	window['AscCommonExcel'].g_oUndoRedoPivotTables = null;
})(window);
