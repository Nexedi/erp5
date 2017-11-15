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
/**
 * User: Ilja.Kirillov
 * Date: 03.05.2017
 * Time: 12:12
 */

var sdtlock_ContentLocked    = 0x00;
var sdtlock_SdtContentLocked = 0x01;
var sdtlock_SdtLocked        = 0x02;
var sdtlock_Unlocked         = 0x03;

var sdttype_BlockLevel  = 0x01;
var sdttype_InlineLevel = 0x02;
var sdttype_RowLevel    = 0x03;
var sdttype_CellLevel   = 0x04;

function CSdtPr()
{
	this.Alias = undefined;
	this.Id    = undefined;
	this.Tag   = undefined;
	this.Label = undefined;
	this.Lock  = undefined;
}

CSdtPr.prototype.Copy = function()
{
	var oPr = new CSdtPr();

	oPr.Alias = this.Alias;
	oPr.Id    = this.Id;
	oPr.Tag   = this.Tag;
	oPr.Label = this.Label;
	oPr.Lock  = this.Lock;

	return oPr;
};
CSdtPr.prototype.Write_ToBinary = function(Writer)
{
	var StartPos = Writer.GetCurPosition();
	Writer.Skip(4);
	var Flags = 0;

	if (undefined !== this.Alias)
	{
		Writer.WriteString2(this.Alias);
		Flags |= 1;
	}

	if (undefined !== this.Id)
	{
		Writer.WriteLong(this.Id);
		Flags |= 2;
	}

	if (undefined !== this.Tag)
	{
		Writer.WriteString2(this.Tag);
		Flags |= 4;
	}

	if (undefined !== this.Label)
	{
		Writer.WriteLong(this.Tag);
		Flags |= 8;
	}

	if (undefined !== this.Lock)
	{
		Writer.WriteLong(this.Lock);
		Flags |= 16;
	}

	var EndPos = Writer.GetCurPosition();
	Writer.Seek( StartPos );
	Writer.WriteLong( Flags );
	Writer.Seek( EndPos );
};
CSdtPr.prototype.Read_FromBinary = function(Reader)
{
	var Flags = Reader.GetLong();

	if (Flags & 1)
		this.Alias = Reader.GetString2();

	if (Flags & 2)
		this.Id = Reader.GetLong();

	if (Flags & 4)
		this.Tag = Reader.GetString2();

	if (Flags & 8)
		this.Tag = Reader.GetLong();

	if (Flags & 16)
		this.Lock = Reader.GetLong();
};

function CContentControlPr()
{
	this.Id         = undefined;
	this.Tag        = undefined;
	this.Lock       = undefined;
	this.InternalId = undefined;
}
CContentControlPr.prototype.get_Id = function()
{
	return this.Id;
};
CContentControlPr.prototype.put_Id = function(Id)
{
	this.Id = Id;
};
CContentControlPr.prototype.get_Tag = function()
{
	return this.Tag;
};
CContentControlPr.prototype.put_Tag = function(sTag)
{
	this.Tag = sTag;
};
CContentControlPr.prototype.get_Lock = function()
{
	return this.Lock;
};
CContentControlPr.prototype.put_Lock = function(nLock)
{
	this.Lock = nLock;
};
CContentControlPr.prototype.get_InternalId = function()
{
	return this.InternalId;
};

//--------------------------------------------------------export--------------------------------------------------------
window['AscCommonWord']        = window['AscCommonWord'] || {};
window['AscCommonWord'].CSdtPr = CSdtPr;

window['AscCommonWord'].sdtlock_Unlocked         = sdtlock_Unlocked;
window['AscCommonWord'].sdtlock_ContentLocked    = sdtlock_ContentLocked;
window['AscCommonWord'].sdtlock_SdtContentLocked = sdtlock_SdtContentLocked;
window['AscCommonWord'].sdtlock_SdtLocked        = sdtlock_SdtLocked;

window['AscCommonWord'].sdttype_BlockLevel  = sdttype_BlockLevel;
window['AscCommonWord'].sdttype_InlineLevel = sdttype_InlineLevel;
window['AscCommonWord'].sdttype_RowLevel    = sdttype_RowLevel;
window['AscCommonWord'].sdttype_CellLevel   = sdttype_CellLevel;

window['AscCommonWord'].CContentControlPr = CContentControlPr;

CContentControlPr.prototype['get_Id']         = CContentControlPr.prototype.get_Id;
CContentControlPr.prototype['put_Id']         = CContentControlPr.prototype.put_Id;
CContentControlPr.prototype['get_Tag']        = CContentControlPr.prototype.get_Tag;
CContentControlPr.prototype['put_Tag']        = CContentControlPr.prototype.put_Tag;
CContentControlPr.prototype['get_Lock']       = CContentControlPr.prototype.get_Lock;
CContentControlPr.prototype['put_Lock']       = CContentControlPr.prototype.put_Lock;
CContentControlPr.prototype['get_InternalId'] = CContentControlPr.prototype.get_InternalId;

